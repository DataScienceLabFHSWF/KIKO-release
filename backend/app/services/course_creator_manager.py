# backend/app/services/course_creator_manager.py
import os, time, asyncio, re, yaml
from copy import deepcopy
from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.schemas import QuestionAnswerList
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from typing import Dict, Any, List, Tuple
from app.models import (
    CourseModel, QuizModel, QuestionModel, ExamModel,
    ExamQuestionModel, ExamSubmissionModel, ExamAnswerModel,
    LearnerCourseProgressModel
)
from app.utils import rewrite_markdown_image_urls, lang_display

load_dotenv()
DOCKER_OLLAMA_URL = os.getenv("DOCKER_OLLAMA_URL")
CC_MAP_PROMPT_NAME = "cc_batch_map_summary_prompt"
CC_REDUCE_PROMPT_NAME = "cc_batch_reduce_summary_prompt"
CC_QUESTION_PROMPT_NAME = "cc_batch_question_prompt"
CC_QUIZ_PROMPT_NAME = "cc_batch_quiz_prompt"
CC_TITLE_PROMPT_NAME = "cc_batch_title_prompt"
KIKO_MD_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "core", "templates")


def _slugify(value: str) -> str:
    """Convert a title into a safe, deterministic slug for IDs/file names.

    Keeps lowercase ASCII letters/numbers, collapses spaces/underscores/hyphens
    into single hyphens, and returns a stable fallback when input is empty.
    """
    normalized = (value or "").strip().lower()
    normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
    normalized = re.sub(r"[\s_-]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized)
    return normalized.strip("-") or "generated-course"


def _looks_like_hash(value: str) -> bool:
    """Return True when a value resembles a long hex hash token.

    Used to avoid treating storage/hash-based filenames as human-friendly titles.
    """
    normalized = (value or "").strip().lower()
    return bool(re.fullmatch(r"[a-f0-9]{32,}", normalized))


def _derive_course_title(source_filename: str, summary_text: str) -> str:
    """Derive a readable fallback title from filename, then summary.

    Priority:
    1) Filename stem (when it is not hash-like), normalized for readability.
    2) First summary line, trimmed to a safe length.
    3) Static fallback title.
    """
    stem = os.path.splitext(os.path.basename(source_filename or ""))[0]
    stem_title = stem.replace("_", " ").replace("-", " ").strip().title()
    if stem_title and not _looks_like_hash(stem):
        return stem_title

    first_line = (summary_text or "").strip().splitlines()
    if first_line:
        fallback = first_line[0].strip("# ").strip()
        if fallback:
            return fallback[:100]
    return "Generated Course"


def _sanitize_course_title(raw_title: str, max_words: int = 8, max_chars: int = 60) -> str:
    """Normalize and enforce compact title limits for UI/metadata stability.

    Collapses whitespace, strips leading/trailing punctuation, limits word count
    and character length, and guarantees a non-empty fallback title.
    """
    title = re.sub(r"\s+", " ", str(raw_title or "").strip())
    title = re.sub(r"^[\-–—:;,.\s]+|[\-–—:;,.\s]+$", "", title)

    if not title:
        return "Generated Course"

    words = title.split()
    if len(words) > max_words:
        title = " ".join(words[:max_words])

    if len(title) > max_chars:
        title = title[:max_chars].rstrip(" -–—:;,")

    title = re.sub(r"\s+", " ", title).strip()
    return title or "Generated Course"


def _derive_stable_slug_suffix(source_filename: str, max_chars: int = 8) -> str:
    """Return a short stable suffix for slug uniqueness when source stem is hash-like."""
    stem = os.path.splitext(os.path.basename(source_filename or ""))[0].strip().lower()
    if _looks_like_hash(stem):
        return stem[:max_chars]
    return ""


def _template_require(mapping: Dict[str, Any], path: str, expected_type: type) -> Any:
    current: Any = mapping
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            raise ValueError(f"Missing required template key: {path}")
        current = current[segment]
    if not isinstance(current, expected_type):
        raise ValueError(
            f"Template key '{path}' must be of type {expected_type.__name__}"
        )
    return current


def _load_kiko_downloadable_template(language_code: str) -> Dict[str, Any]:
    template_file_name = "kiko_markdown_structure_prefilled_data_de.yml" if language_code == "de" else "kiko_markdown_structure_prefilled_data_en.yml"
    template_path = os.path.normpath(os.path.join(KIKO_MD_TEMPLATE_DIR, template_file_name))

    if not os.path.exists(template_path):
        raise ValueError(f"Markdown template file not found: {template_path}")

    try:
        with open(template_path, "r", encoding="utf-8") as template_file:
            parsed = yaml.safe_load(template_file)
    except Exception as exc:
        raise ValueError(f"Failed to read markdown template {template_path}: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"Invalid markdown template format in {template_path}: expected YAML mapping")

    required_fields: list[tuple[str, type]] = [
        ("front_matter", dict),
        ("front_matter.course", dict),
        ("front_matter.instructors", list),
        ("front_matter.grading", dict),
        ("front_matter.resources", list),
        ("content", dict),
        ("content.no_summary", str),
        ("content.headings", dict),
        ("content.headings.course_overview", str),
        ("content.headings.learning_outcomes", str),
        ("content.headings.modules", str),
        ("content.headings.module_1_title", str),
        ("content.headings.overall_quiz", str),
        ("content.headings.content", str),
        ("content.headings.questions", str),
        ("content.headings.quiz", str),
        ("content.headings.further_reading", str),
        ("content.headings.misconceptions", str),
        ("content.headings.grade", str),
        ("content.learning_outcomes", list),
        ("content.further_reading", list),
        ("content.misconceptions", list),
        ("defaults", dict),
        ("defaults.qa", dict),
        ("defaults.qa.id_prefix", str),
        ("defaults.qa.points", int),
        ("defaults.quiz", dict),
        ("defaults.quiz.meta", dict),
        ("defaults.quiz.meta.id", str),
        ("defaults.quiz.meta.title", str),
        ("defaults.quiz.meta.pass_percent", int),
        ("defaults.quiz.item", dict),
        ("defaults.quiz.item.id_prefix", str),
        ("defaults.quiz.item.type", str),
        ("defaults.quiz.item.points", int),
        ("defaults.grade", dict),
        ("defaults.grade.completion", dict),
        ("defaults.grade.completion.required", bool),
        ("defaults.grade.completion.passing_percent", int),
        ("defaults.grade.grade_item_id", str),
    ]

    for path, expected_type in required_fields:
        _template_require(parsed, path, expected_type)

    return parsed

class AsyncBatchProcessor:
    def __init__(
        self,
        prompt_manager, 
        llm_model_name,
        response_language, 
        batch_size=10000, 
        chunk_overlap=300, 
        max_concurrency=20
    ):
        self.prompt_manager = prompt_manager
        self.llm = OllamaLLM(
            model=llm_model_name,
            temperature=0,
            base_url=DOCKER_OLLAMA_URL,
        )   
        self.batch_size = batch_size
        self.chunk_overlap = chunk_overlap
        self.max_concurrency = max_concurrency
        self.response_language = response_language

        self._initialize_chains()
    
    def _load_prompt(self, prompt_name: str) -> str:
        template = self.prompt_manager.load_prompt_template(
            prompt_name,
            lang=self.response_language
        )
        if not template:
            raise ValueError(
                f"❌ Prompt template not found: {prompt_name} (lang={self.response_language})"
            )
        return template
    
    def _extract_json_object(self, raw_output) -> str:
        """Extract the first top-level JSON object from model output."""
        if hasattr(raw_output, "content"):
            text = raw_output.content
        else:
            text = str(raw_output)
        
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        
        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"❌ No complete JSON object found in model output: {text}")
        
        return text[start:end + 1]

    def _extract_yaml_content(self, raw_output: Any) -> str:
        """Extract YAML payload from model output, accepting fenced or raw YAML."""
        if hasattr(raw_output, "content"):
            text = raw_output.content
        else:
            text = str(raw_output)

        text = text.strip()
        fenced_match = re.search(r"```(?:yaml|yml)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if fenced_match:
            return fenced_match.group(1).strip()
        return text

    def _normalize_quiz_yaml(
        self,
        quiz_yaml_text: str,
        expected_question_count: int,
        expected_option_count: int,
    ) -> str:
        """Validate and normalize generated quiz YAML."""
        parsed = yaml.safe_load(quiz_yaml_text)
        if not isinstance(parsed, dict):
            raise ValueError("Generated quiz must be a YAML mapping")

        meta = parsed.get("meta")
        items = parsed.get("items")
        if not isinstance(meta, dict):
            raise ValueError("Generated quiz YAML must include a 'meta' mapping")
        if not isinstance(items, list) or not items:
            raise ValueError("Generated quiz YAML must include a non-empty 'items' list")

        if len(items) != expected_question_count:
            raise ValueError(
                f"Generated quiz must include exactly {expected_question_count} items"
            )

        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                raise ValueError(f"Quiz item #{index} must be a mapping")

            item_type = str(item.get("type") or "").strip().lower()
            if item_type != "mcq":
                raise ValueError(f"Quiz item #{index} must be type 'mcq'")

            choices = item.get("choices")
            if not isinstance(choices, list) or len(choices) != expected_option_count:
                raise ValueError(
                    f"Quiz item #{index} must have exactly {expected_option_count} choices"
                )

            correct_count = 0
            for choice_index, choice in enumerate(choices, start=1):
                if not isinstance(choice, dict):
                    raise ValueError(
                        f"Quiz item #{index} choice #{choice_index} must be a mapping"
                    )
                correct_flag = choice.get("correct")
                if correct_flag is True:
                    correct_count += 1
                elif correct_flag not in (False, None):
                    raise ValueError(
                        f"Quiz item #{index} choice #{choice_index} has invalid 'correct' value"
                    )

            if correct_count != 1:
                raise ValueError(
                    f"Quiz item #{index} must have exactly one correct choice"
                )

        return yaml.safe_dump(parsed, sort_keys=False, allow_unicode=True).strip()
    
    def _initialize_chains(self):
        map_prompt_template = self._load_prompt(CC_MAP_PROMPT_NAME)
        reduce_prompt_template = self._load_prompt(CC_REDUCE_PROMPT_NAME)
        question_prompt_template = self._load_prompt(CC_QUESTION_PROMPT_NAME)
        quiz_prompt_template = self._load_prompt(CC_QUIZ_PROMPT_NAME)
        title_prompt_template = self._load_prompt(CC_TITLE_PROMPT_NAME)
        
        self.map_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=map_prompt_template,
                input_variables=["text"],
                partial_variables={"response_language": lang_display(self.response_language)}
            )
        )

        self.reduce_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=reduce_prompt_template,
                input_variables=["text"],
                partial_variables={"response_language": lang_display(self.response_language)}
            )
        )

        # Create Pydantic parser
        self.qa_parser = PydanticOutputParser(pydantic_object=QuestionAnswerList)
        format_instructions = self.qa_parser.get_format_instructions()

        # Pipeline: Prompt -> LLM -> Parser
        self.question_chain = (
            PromptTemplate(
                template=question_prompt_template,
                input_variables=["text", "qa_count"],
                partial_variables={
                    "format_instructions": format_instructions,
                    "response_language": lang_display(self.response_language)
                }
            )
            | self.llm
            | RunnableLambda(self._extract_json_object)
            | self.qa_parser
        )

        self.quiz_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=quiz_prompt_template,
                input_variables=["generated_summary", "quiz_question_count", "quiz_option_count"],
                partial_variables={"response_language": lang_display(self.response_language)}
            )
        )

        self.title_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=title_prompt_template,
                input_variables=["generated_summary"],
                partial_variables={"response_language": lang_display(self.response_language)}
            )
        )

    async def generate_short_course_title(
        self,
        generated_summary: str,
        source_filename: str,
    ) -> str:
        fallback_title = _sanitize_course_title(
            _derive_course_title(source_filename=source_filename, summary_text=generated_summary)
        )

        if not isinstance(generated_summary, str) or not generated_summary.strip():
            return fallback_title

        try:
            title_result = await asyncio.wait_for(
                self.title_chain.ainvoke(
                    {
                        "generated_summary": generated_summary,
                    }
                ),
                timeout=45,
            )
            candidate = str((title_result or {}).get("text") or "").strip()
            candidate = candidate.splitlines()[0].strip() if candidate else ""
            candidate = _sanitize_course_title(candidate)
            return candidate or fallback_title
        except Exception as exc:
            print(f"⚠️ Title generation failed; falling back to filename/summary title: {exc}")
            return fallback_title

    async def generate_structured_quiz_yaml(
        self,
        generated_summary: str,
        quiz_question_count: int = 3,
        quiz_option_count: int = 3,
    ) -> str:
        """Generate strict YAML quiz structure from a generated summary using the same LLM."""
        if not isinstance(generated_summary, str) or not generated_summary.strip():
            raise ValueError("generated_summary must be a non-empty string")

        if quiz_question_count < 1 or quiz_question_count > 4:
            raise ValueError("quiz_question_count must be between 1 and 4")
        if quiz_option_count < 2 or quiz_option_count > 4:
            raise ValueError("quiz_option_count must be between 2 and 4")

        quiz_result = await self.quiz_chain.ainvoke(
            {
                "generated_summary": generated_summary,
                "quiz_question_count": quiz_question_count,
                "quiz_option_count": quiz_option_count,
            }
        )
        raw_quiz_text = quiz_result.get("text", "")
        yaml_text = self._extract_yaml_content(raw_quiz_text)
        return self._normalize_quiz_yaml(
            yaml_text,
            expected_question_count=quiz_question_count,
            expected_option_count=quiz_option_count,
        )

    async def process_chunk(self, chunk: Dict, semaphore: asyncio.Semaphore) -> str:
        async with semaphore:
            for attempt in range(3):
                try:
                    result = await self.map_chain.ainvoke({"text": chunk})
                    return result.get('text', "")
                except Exception as e:
                    if attempt == 2:
                        print(f"Chunk failed after retries: {e}")
                        return ""
                    await asyncio.sleep(1)

    async def batch_reduce(self, summaries):
        """
        Public entrypoint: reduces an arbitrary‑length list of summaries
        down to a single final summary.
        """
        return await self._hierarchical_reduce(summaries)

    async def _hierarchical_reduce(self, batches, group_size=10):
        """
        Recursively folds `batches` (a list of strings) in groups of
        `group_size` until only one summary remains.
        """
        # Base case: one (or zero) summaries left
        if len(batches) <= 1:
            return batches[0] if batches else ""

        next_round = []
        for i in range(0, len(batches), group_size):
            chunk = batches[i : i + group_size]
            result = await self.reduce_chain.ainvoke({
                "text": "\n\n".join(chunk)
            })
            next_round.append(result.get("text", ""))

        # Recurse on the smaller list
        return await self._hierarchical_reduce(next_round, group_size)


    async def summarize_document(
        self,
        path: str,
        qa_count: int = 5,
        quiz_question_count: int = 3,
        quiz_option_count: int = 3,
    ) -> Dict[str, Any]:
        if qa_count < 1 or qa_count > 10:
            raise ValueError("qa_count must be between 1 and 10")

        start_time = time.time()

        loader = PyMuPDFLoader(path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.batch_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        chunks = splitter.split_documents(docs)
        print(f"Document split into {len(chunks)} chunks.")

        if len(chunks) == 1:
            print("Single chunk detected. Using reduce on original content.")
            reduce_input = chunks[0].page_content
            reduce_out = await self.reduce_chain.ainvoke({"text": reduce_input})
            final_summary = reduce_out.get("text", "")
        else:
            semaphore = asyncio.Semaphore(self.max_concurrency)
            tasks = [
                self.process_chunk(chunk.page_content, semaphore)
                for chunk in chunks
            ]
            summaries = await asyncio.gather(*tasks)
            summaries = [s for s in summaries if s]

            print("Generating final summary...")
            final_summary = await self.batch_reduce(summaries)

        generated_quiz = None
        try:
            print("Generating structured quiz YAML...")
            generated_quiz = await asyncio.wait_for(
                self.generate_structured_quiz_yaml(
                    final_summary,
                    quiz_question_count=quiz_question_count,
                    quiz_option_count=quiz_option_count,
                ),
                timeout=180,
            )
        except asyncio.TimeoutError:
            print("⚠️ Quiz generation timed out after 180s; continuing without quiz.")
        except Exception as exc:
            print(f"⚠️ Quiz generation failed: {exc}")

        print("Generating questions...")
        qa_list_obj: QuestionAnswerList = await self.question_chain.ainvoke(
            {
                "text": final_summary,
                "qa_count": qa_count,
            }
        )
        questions_dict = qa_list_obj.model_dump()  # Convert to dict

        processing_time = round(time.time() - start_time, 2)
        print(f"Total processing time: {processing_time} seconds")

        generated_course_title = await self.generate_short_course_title(
            generated_summary=final_summary,
            source_filename=os.path.basename(path),
        )

        slug_suffix = _derive_stable_slug_suffix(os.path.basename(path))
        markdown_slug = _slugify(generated_course_title)
        if slug_suffix:
            markdown_slug = f"{markdown_slug}-{slug_suffix}"

        markdown_file_name = f"{markdown_slug}.md"
        generated_markdown = self.build_kiko_markdown_document(
            source_filename=os.path.basename(path),
            summary_text=final_summary,
            questions_dict=questions_dict,
            quiz_yaml_text=generated_quiz,
            course_title_override=generated_course_title,
            slug_suffix=slug_suffix,
        )

        return {
            "final_summary": final_summary,
            "questions": questions_dict,
            "quiz": generated_quiz,
            "generated_markdown": generated_markdown,
            "generated_markdown_file_name": markdown_file_name,
            "processing_time_seconds": processing_time
        }

    async def summarize_text(
        self,
        text: str,
        qa_count: int = 5,
        quiz_question_count: int = 3,
        quiz_option_count: int = 3,
    ) -> Dict[str, Any]:
        start_time = time.time()

        if qa_count < 1 or qa_count > 10:
            raise ValueError("qa_count must be between 1 and 10")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.batch_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        chunks = splitter.split_text(text or "")
        print(f"Raw text split into {len(chunks)} chunks.")

        if len(chunks) == 1:
            print("Single chunk text. Using reduce on original text.")
            reduce_out = await self.reduce_chain.ainvoke({"text": text or ""})
            final_summary = reduce_out.get("text", "")
        else:
            semaphore = asyncio.Semaphore(self.max_concurrency)
            tasks = [self.process_chunk(chunk, semaphore) for chunk in chunks]
            summaries = await asyncio.gather(*tasks)
            summaries = [s for s in summaries if s]

            print("Generating final summary (text)...")
            final_summary = await self.batch_reduce(summaries)

        generated_quiz = None
        try:
            print("Generating structured quiz YAML (text)...")
            generated_quiz = await asyncio.wait_for(
                self.generate_structured_quiz_yaml(
                    final_summary,
                    quiz_question_count=quiz_question_count,
                    quiz_option_count=quiz_option_count,
                ),
                timeout=180,
            )
        except asyncio.TimeoutError:
            print("⚠️ Quiz generation timed out after 180s (text); continuing without quiz.")
        except Exception as exc:
            print(f"⚠️ Quiz generation failed (text): {exc}")

        print("Generating questions (text)...")
        qa_list_obj: QuestionAnswerList = await self.question_chain.ainvoke(
            {
                "text": final_summary,
                "qa_count": qa_count,
            }
        )
        questions_dict = qa_list_obj.model_dump()

        processing_time = round(time.time() - start_time, 2)
        print(f"Total processing time (text): {processing_time} seconds")

        return {
            "final_summary": final_summary,
            "questions": questions_dict,
            "quiz": generated_quiz,
            "processing_time_seconds": processing_time
        }

    def build_kiko_markdown_document(
        self,
        source_filename: str,
        summary_text: str,
        questions_dict: Dict[str, Any],
        quiz_yaml_text: str | None,
        course_title_override: str | None = None,
        slug_suffix: str | None = None,
    ) -> str:
        language_code = "de" if self.response_language == "de" else "en"
        template = _load_kiko_downloadable_template(language_code)

        front_matter_template = _template_require(template, "front_matter", dict)
        content_template = _template_require(template, "content", dict)
        defaults_template = _template_require(template, "defaults", dict)

        course_defaults = _template_require(front_matter_template, "course", dict)
        instructors_defaults = _template_require(front_matter_template, "instructors", list)
        grading_defaults = _template_require(front_matter_template, "grading", dict)
        resources_defaults = _template_require(front_matter_template, "resources", list)

        headings = _template_require(content_template, "headings", dict)
        learning_outcomes = _template_require(content_template, "learning_outcomes", list)
        further_reading = _template_require(content_template, "further_reading", list)
        misconceptions = _template_require(content_template, "misconceptions", list)
        no_summary_text = _template_require(content_template, "no_summary", str)

        qa_defaults = _template_require(defaults_template, "qa", dict)
        quiz_defaults = _template_require(defaults_template, "quiz", dict)
        quiz_meta_defaults = _template_require(quiz_defaults, "meta", dict)
        quiz_item_defaults = _template_require(quiz_defaults, "item", dict)
        grade_defaults = _template_require(defaults_template, "grade", dict)
        grade_completion_defaults = _template_require(grade_defaults, "completion", dict)

        qa_id_prefix = _template_require(qa_defaults, "id_prefix", str)
        qa_points_default = _template_require(qa_defaults, "points", int)
        quiz_meta_id_default = _template_require(quiz_meta_defaults, "id", str)
        quiz_meta_title_default = _template_require(quiz_meta_defaults, "title", str)
        quiz_meta_pass_default = _template_require(quiz_meta_defaults, "pass_percent", int)
        quiz_item_id_prefix = _template_require(quiz_item_defaults, "id_prefix", str)
        quiz_item_type_default = _template_require(quiz_item_defaults, "type", str)
        quiz_item_points_default = _template_require(quiz_item_defaults, "points", int)
        grade_required_default = _template_require(grade_completion_defaults, "required", bool)
        grade_pass_default = _template_require(grade_completion_defaults, "passing_percent", int)
        grade_item_id_default = _template_require(grade_defaults, "grade_item_id", str)

        course_overview_heading = _template_require(headings, "course_overview", str)
        learning_outcomes_heading = _template_require(headings, "learning_outcomes", str)
        modules_heading = _template_require(headings, "modules", str)
        module_1_title = _template_require(headings, "module_1_title", str)
        overall_quiz_heading = _template_require(headings, "overall_quiz", str)
        content_heading = _template_require(headings, "content", str)
        questions_heading = _template_require(headings, "questions", str)
        quiz_heading = _template_require(headings, "quiz", str)
        further_reading_heading = _template_require(headings, "further_reading", str)
        misconceptions_heading = _template_require(headings, "misconceptions", str)
        grade_heading = _template_require(headings, "grade", str)

        if course_title_override and str(course_title_override).strip():
            course_title = _sanitize_course_title(str(course_title_override))
        else:
            course_title = _sanitize_course_title(_derive_course_title(source_filename, summary_text))
        course_slug = _slugify(course_title)

        normalized_suffix = re.sub(r"[^a-z0-9]", "", str(slug_suffix or "").strip().lower())
        if normalized_suffix:
            course_slug = f"{course_slug}-{normalized_suffix}"

        source_doc_name = f"{course_slug}.md"

        qa_list = (questions_dict or {}).get("qa_list") or []
        qa_items: list[dict[str, Any]] = []
        for index, item in enumerate(qa_list, start=1):
            question_text = str((item or {}).get("question") or "").strip()
            answer_text = str((item or {}).get("answer") or "").strip()
            if not question_text and not answer_text:
                continue
            qa_items.append(
                {
                    "id": f"{qa_id_prefix}{index}",
                    "prompt": question_text or "",
                    "reference_answer": answer_text or "",
                    "points": qa_points_default,
                }
            )

        if not qa_items:
            fallback_question = "What is one key concept from this module?" if self.response_language != "de" else "Was ist ein zentrales Konzept dieses Moduls?"
            fallback_answer = "A concise explanation from the module content." if self.response_language != "de" else "Eine kurze Erklärung aus dem Modulinhalt."
            qa_items.append(
                {
                    "id": f"{qa_id_prefix}1",
                    "prompt": fallback_question,
                    "reference_answer": fallback_answer,
                    "points": qa_points_default,
                }
            )

        quiz_dict: Dict[str, Any]
        if quiz_yaml_text and str(quiz_yaml_text).strip():
            parsed_quiz = yaml.safe_load(quiz_yaml_text)
            quiz_dict = parsed_quiz if isinstance(parsed_quiz, dict) else {
                "meta": {
                    "id": quiz_meta_id_default,
                    "title": quiz_meta_title_default,
                    "pass_percent": quiz_meta_pass_default,
                },
                "items": [],
            }
        else:
            quiz_dict = {
                "meta": {
                    "id": quiz_meta_id_default,
                    "title": quiz_meta_title_default,
                    "pass_percent": quiz_meta_pass_default,
                },
                "items": [],
            }

        if not isinstance(quiz_dict.get("meta"), dict):
            quiz_dict["meta"] = {
                "id": quiz_meta_id_default,
                "title": quiz_meta_title_default,
                "pass_percent": quiz_meta_pass_default,
            }

        quiz_dict["meta"].setdefault("id", quiz_meta_id_default)
        quiz_dict["meta"].setdefault("title", quiz_meta_title_default)
        quiz_dict["meta"].setdefault("pass_percent", quiz_meta_pass_default)

        quiz_items = quiz_dict.get("items")
        if not isinstance(quiz_items, list):
            quiz_items = []
            quiz_dict["items"] = quiz_items

        for index, quiz_item in enumerate(quiz_items, start=1):
            if not isinstance(quiz_item, dict):
                continue
            quiz_item.setdefault("id", f"{quiz_item_id_prefix}{index}")
            quiz_item.setdefault("type", quiz_item_type_default)
            quiz_item.setdefault("points", quiz_item_points_default)

        if not quiz_items:
            fallback_prompt = "Which statement best reflects the module summary?" if self.response_language != "de" else "Welche Aussage entspricht am besten der Modulinhaltszusammenfassung?"
            fallback_choice_1 = "It captures a core idea from the module." if self.response_language != "de" else "Sie fasst eine Kernidee des Moduls zusammen."
            fallback_choice_2 = "It is unrelated to the module." if self.response_language != "de" else "Sie hat keinen Bezug zum Modul."
            quiz_items.append(
                {
                    "id": f"{quiz_item_id_prefix}1",
                    "type": quiz_item_type_default,
                    "prompt": fallback_prompt,
                    "choices": [
                        {"id": "a", "text": fallback_choice_1, "correct": True},
                        {"id": "b", "text": fallback_choice_2, "correct": False},
                    ],
                    "points": quiz_item_points_default,
                }
            )

        front_matter = {
            "schema": "course.v1",
            "course": {
                "id": course_slug,
                "source_doc": source_doc_name,
                "title": course_title,
                "version": _template_require(course_defaults, "version", str),
                "provider": _template_require(course_defaults, "provider", str),
                "language": _template_require(course_defaults, "language", str),
                "level": _template_require(course_defaults, "level", str),
                "tags": deepcopy(_template_require(course_defaults, "tags", list)),
                "estimated_minutes": _template_require(course_defaults, "estimated_minutes", int),
                "published": _template_require(course_defaults, "published", bool),
                "prerequisites": deepcopy(_template_require(course_defaults, "prerequisites", list)),
            },
            "instructors": deepcopy(instructors_defaults),
            "grading": deepcopy(grading_defaults),
            "resources": deepcopy(resources_defaults),
        }

        front_matter_text = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True).strip()
        qa_yaml_text = yaml.safe_dump(qa_items, sort_keys=False, allow_unicode=True).strip() if qa_items else "[]"
        quiz_yaml_block = yaml.safe_dump(quiz_dict, sort_keys=False, allow_unicode=True).strip()
        misconceptions_yaml_block = yaml.safe_dump(misconceptions, sort_keys=False, allow_unicode=True).strip()

        learning_outcomes_text = "\n".join(f"- {str(item)}" for item in learning_outcomes if str(item).strip())
        if not learning_outcomes_text:
            raise ValueError("Template key 'content.learning_outcomes' must contain at least one non-empty value")

        further_reading_text = "\n".join(f"- {str(item)}" for item in further_reading if str(item).strip())
        if not further_reading_text:
            raise ValueError("Template key 'content.further_reading' must contain at least one non-empty value")

        summary_clean = (summary_text or "").strip() or no_summary_text

        return (
            f"---\n{front_matter_text}\n---\n\n"
            "<!-- Course contents start -->\n\n"
            f"# {course_title}\n\n"
            f"## {course_overview_heading}\n\n"
            f"{summary_clean}\n\n"
            f"### {learning_outcomes_heading}\n\n"
            f"{learning_outcomes_text}\n\n"
            f"## {modules_heading}\n\n"
            f"### {module_1_title}\n\n"
            f"#### {content_heading}\n\n"
            f"{summary_clean}\n\n"
            f"#### {questions_heading}\n\n"
            "```yaml\n"
            f"{qa_yaml_text}\n"
            "```\n\n"
            f"#### {quiz_heading}\n\n"
            "```yaml\n"
            f"{quiz_yaml_block}\n"
            "```\n\n"
            f"#### {further_reading_heading}\n\n"
            f"{further_reading_text}\n\n"
            f"#### {misconceptions_heading}\n\n"
            "```yaml\n"
            f"{misconceptions_yaml_block}\n"
            "```\n\n"
            f"#### {grade_heading}\n\n"
            "```yaml\n"
            "completion:\n"
            f"  required: {str(grade_required_default).lower()}\n"
            f"  passing_percent: {grade_pass_default}\n"
            "grade_items:\n"
            f"  - id: {grade_item_id_default}\n"
            f"    points_total: {len(quiz_items) if isinstance(quiz_items, list) else 0}\n"
            "```\n\n"
            f"## {overall_quiz_heading}\n\n"
            "```yaml\n"
            f"{quiz_yaml_block}\n"
            "```\n\n"
            "<!-- Course contents End -->\n"
        )


async def list_courses_for_instructor(user_id: int, db: AsyncSession) -> list[Dict[str, Any]]:
    try:
        result = await db.execute(
            select(CourseModel)
            .options(joinedload(CourseModel.quiz))
            .where(CourseModel.created_by == user_id)
        )
        courses = result.scalars().all()

        if not courses:
            return []

        counts_result = await db.execute(
            select(QuestionModel.course_id, func.count())
            .select_from(QuestionModel)
            .where(QuestionModel.course_id.in_([c.course_id for c in courses]))
            .group_by(QuestionModel.course_id)
        )
        counts_map = {cid: cnt for cid, cnt in counts_result.all()}

        return [
            {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
                "quiz": course.quiz.content if course.quiz else None,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "question_count": counts_map.get(course.course_id, 0),
                "is_template": getattr(course, "is_template", False),
                "has_course_json": bool(getattr(course, "course_json", None)),
                "has_template_markdown": bool(getattr(course, "template_markdown", None)),
            }
            for course in courses
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while listing courses for user {user_id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while listing courses for user {user_id}: {str(e)}"
        )


async def get_course_detail_for_instructor(course_id: int, user_id: int, db: AsyncSession) -> Dict[str, Any]:
    try:
        result = await db.execute(
            select(CourseModel)
            .options(
                joinedload(CourseModel.questions), 
                joinedload(CourseModel.quiz)
            )
            .where(CourseModel.course_id == course_id)
        )
        course = result.scalars().first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Course not found"
            )
        if course.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Forbidden"
            )

        return {
            "course": {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
                "quiz": course.quiz.content if course.quiz else None,
                "created_at": course.created_at.isoformat() if course.created_at else None,
            },
            "questions": [
                {
                    "question_id": question.question_id,
                    "text": question.text,
                    "answer_text": question.answer_text,
                }
                for question in (course.questions or [])
            ],
            "course_json": course.course_json or {},
            "template_markdown": course.template_markdown or "",
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while fetching course {course_id} detail for user {user_id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while fetching course {course_id} detail for user {user_id}: {str(e)}"
        )

def rewrite_course_json_markdown_fields(
    course_json: Dict[str, Any],
    course_id: int,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Rewrite markdown image URLs inside parsed course_json so learner/instructor
    rendering can use backend-served image URLs consistently.

    Rewrites:
    - overview_md
    - each module.content_md
    - each module.further_reading_md

    Returns:
      (rewritten_course_json, referenced_images)
    """
    if not isinstance(course_json, dict):
        return course_json, []

    rewritten = deepcopy(course_json)
    referenced_images: set[str] = set()

    def _rewrite_field(container: Dict[str, Any], key: str) -> None:
        value = container.get(key)
        if isinstance(value, str) and value.strip():
            rewritten_value, refs = rewrite_markdown_image_urls(value, course_id)
            container[key] = rewritten_value
            if refs:
                referenced_images.update(refs)

    _rewrite_field(rewritten, "overview_md")

    modules = rewritten.get("modules")
    if isinstance(modules, list):
        for module in modules:
            if isinstance(module, dict):
                _rewrite_field(module, "content_md")
                _rewrite_field(module, "further_reading_md")

    return rewritten, sorted(referenced_images)

async def create_course_with_summary_and_qas_for_instructor(
    title: str,
    summary: str,
    questions: List[Dict[str, Any]],
    user_id: int,
    db: AsyncSession,
    quiz: str | None = None,
    template_markdown: str | None = None,
    course_json: dict | None = None,
) -> Dict[str, Any]:
    try:
        if not isinstance(summary, str) or not summary.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Summary is required",
            )

        if not isinstance(questions, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Questions must be a list",
            )

        if quiz is not None and not isinstance(quiz, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Invalid quiz format",
            )

        if template_markdown is not None and not isinstance(template_markdown, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Invalid template_markdown format",
            )

        if course_json is not None and not isinstance(course_json, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Invalid course_json format",
            )

        # Prefer explicit title; otherwise fall back to parsed course_json.course.title
        resolved_title = (title or "").strip()
        if not resolved_title and isinstance(course_json, dict):
            resolved_title = (
                ((course_json.get("course") or {}).get("title") or "").strip()
            )

        if not resolved_title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Title is required",
            )

        course = CourseModel(
            title=resolved_title,
            summary=summary.strip(),
            created_by=user_id,
            template_markdown=None,   # set after we know course_id
            course_json=None,         # set after rewrite
        )
        db.add(course)
        await db.flush()

        # Rewrite markdown image URLs in summary using course_id-based route
        rewritten_summary, referenced_images = rewrite_markdown_image_urls(
            summary.strip(),
            course.course_id,
        )
        course.summary = rewritten_summary

        # Optional: store authored template markdown
        if isinstance(template_markdown, str) and template_markdown.strip():
            rewritten_template_markdown, template_refs = rewrite_markdown_image_urls(
                template_markdown.strip(),
                course.course_id,
            )
            course.template_markdown = rewritten_template_markdown
            if template_refs:
                referenced_images.extend(template_refs)

        # Optional: store parsed course JSON, and rewrite markdown fields inside it
        if isinstance(course_json, dict) and course_json:
            rewritten_course_json, course_json_refs = rewrite_course_json_markdown_fields(
                course_json,
                course.course_id,
            )
            course.course_json = rewritten_course_json
            if course_json_refs:
                referenced_images.extend(course_json_refs)
        
        if referenced_images:
            unique_refs = sorted(set(referenced_images))
            print(
                f"ℹ️ Course {course.course_id} references {len(unique_refs)} images: {unique_refs}"
            )

        quiz_content = quiz.strip() if isinstance(quiz, str) and quiz.strip() else None
        
        if quiz_content:
            db.add(
                QuizModel(
                    course_id=course.course_id,
                    content=quiz_content,
                )
            )

        valid_questions_added = 0
        for item in questions:
            if not isinstance(item, dict):
                continue

            text = str(item.get("text") or "").strip()
            answer_text = str(item.get("answer_text") or "").strip()

            if not text or not answer_text:
                continue

            db.add(
                QuestionModel(
                    text=text,
                    answer_text=answer_text,
                    course_id=course.course_id,
                    created_by=user_id,
                )
            )
            valid_questions_added += 1

        await db.commit()
        await db.refresh(course)

        return {
            "message": "Course and QAs saved successfully",
            "course_id": course.course_id,
            "questions_saved": valid_questions_added,
            "has_quiz": bool(quiz_content),
            "has_template_markdown": bool(course.template_markdown),
            "has_course_json": bool(course.course_json),
        }
    except HTTPException:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while creating course for user {user_id}: {str(e)}",
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while creating course for user {user_id}: {str(e)}",
        ) from e

async def update_course_for_instructor(
    course_id: int,
    user_id: int,
    payload: Dict[str, Any],
    db: AsyncSession,
) -> Dict[str, Any]:
    try:
        result = await db.execute(
            select(CourseModel)
            .options(
                joinedload(CourseModel.questions),
                joinedload(CourseModel.quiz),
            )
            .where(CourseModel.course_id == course_id)
        )
        course = result.scalars().first()

        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if course.created_by != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        title = payload.get("title")
        summary = payload.get("summary")
        questions_payload = payload.get("questions")
        quiz_value = payload.get("quiz") if "quiz" in payload else None
        template_markdown = payload.get("template_markdown") if "template_markdown" in payload else None
        course_json_payload = payload.get("course_json") if "course_json" in payload else None

        # -----------------------------
        # title
        # -----------------------------
        if isinstance(title, str) and title.strip():
            course.title = title.strip()
        
        # -----------------------------
        # summary
        # -----------------------------
        if isinstance(summary, str) and summary.strip():
            # Rewrite markdown image URLs when updating summary
            rewritten_summary, referenced_images = rewrite_markdown_image_urls(summary.strip(), course_id)
            course.summary = rewritten_summary
            if referenced_images:
                print(f"ℹ️ Course {course_id} update references {len(referenced_images)} images: {referenced_images}")
        
        # -----------------------------
        # template_markdown
        # -----------------------------
        if "template_markdown" in payload:
            if template_markdown is None:
                course.template_markdown = None
            elif isinstance(template_markdown, str):
                rewritten_template_markdown, referenced_images = rewrite_markdown_image_urls(
                    template_markdown.strip(),
                    course_id,
                )
                course.template_markdown = rewritten_template_markdown

                if referenced_images:
                    print(
                        f"ℹ️ Course {course_id} update references "
                        f"{len(referenced_images)} images in template_markdown: {referenced_images}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid template_markdown format",
                )

        # -----------------------------
        # course_json
        # -----------------------------
        if "course_json" in payload:
            if course_json_payload is None:
                course.course_json = None
            elif isinstance(course_json_payload, dict):
                course.course_json = course_json_payload
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid course_json format",
                )
        
        # -----------------------------
        # quiz
        # -----------------------------
        if "quiz" in payload:
            if isinstance(quiz_value, str):
                stripped_quiz = quiz_value.strip()
                if stripped_quiz:
                    if course.quiz:
                        course.quiz.content = stripped_quiz
                    else:
                        course.quiz = QuizModel(course_id=course.course_id, content=stripped_quiz)
                else:
                    if course.quiz:
                        await db.delete(course.quiz)
                    course.quiz = None
            elif quiz_value is None:
                if course.quiz:
                    await db.delete(course.quiz)
                course.quiz = None
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid quiz format",
                )
        
        # -----------------------------
        # questions
        # -----------------------------
        if questions_payload is not None:
            existing_questions = {q.question_id: q for q in course.questions or []}
            retained_ids: set[int] = set()

            if isinstance(questions_payload, list):
                for item in questions_payload:
                    if not isinstance(item, dict):
                        continue

                    raw_id = item.get("question_id")
                    question_id = None
                    if isinstance(raw_id, int):
                        question_id = raw_id
                    elif raw_id is not None:
                        try:
                            question_id = int(raw_id)
                        except (TypeError, ValueError):
                            raise HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Invalid question_id format: {raw_id}. Must be an integer.",
                            )
                    text = (item.get("text") or "").strip()
                    answer_text = (item.get("answer_text") or "").strip()

                    if question_id is not None and question_id in existing_questions:
                        if text or answer_text:
                            if not text or not answer_text:
                                raise HTTPException(
                                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Question text and answer must both be provided",
                                )
                            question = existing_questions[question_id]
                            question.text = text
                            question.answer_text = answer_text
                            retained_ids.add(question_id)
                        else:
                            # both empty => delete later
                            continue
                    elif text and answer_text:
                        db.add(
                            QuestionModel(
                                text=text,
                                answer_text=answer_text,
                                course_id=course.course_id,
                                created_by=user_id,
                            )
                        )
                    elif text or answer_text:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Question text and answer must both be provided",
                        )

                to_delete = [qid for qid in existing_questions if qid not in retained_ids]
                if to_delete:
                    await db.execute(
                        delete(QuestionModel)
                        .where(
                            QuestionModel.question_id.in_(to_delete)
                        )
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid questions format",
                )

        await db.commit()
        return {"message": "updated", "course_id": course.course_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while updating course {course_id} for user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while updating course {course_id} for user {user_id}: {str(e)}"
        )


async def delete_course_for_instructor(course_id: int, user_id: int, db: AsyncSession) -> Dict[str, Any]:
    try:
        result = await db.execute(select(CourseModel).where(CourseModel.course_id == course_id))
        course = result.scalars().first()

        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if course.created_by != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        exam_ids_res = await db.execute(
            select(ExamModel.exam_id).where(ExamModel.course_id == course.course_id)
        )
        exam_ids = [exam_id for (exam_id,) in exam_ids_res.all()]

        if exam_ids:
            submission_ids_res = await db.execute(
                select(ExamSubmissionModel.submission_id).where(
                    ExamSubmissionModel.exam_id.in_(exam_ids)
                )
            )
            submission_ids = [submission_id for (submission_id,) in submission_ids_res.all()]
            if submission_ids:
                await db.execute(
                    delete(ExamAnswerModel).where(
                        ExamAnswerModel.submission_id.in_(submission_ids)
                    )
                )

            exam_question_ids_res = await db.execute(
                select(ExamQuestionModel.question_id).where(
                    ExamQuestionModel.exam_id.in_(exam_ids)
                )
            )
            exam_question_ids = [question_id for (question_id,) in exam_question_ids_res.all()]
            if exam_question_ids:
                await db.execute(
                    delete(ExamAnswerModel).where(
                        ExamAnswerModel.question_id.in_(exam_question_ids)
                    )
                )

            await db.execute(
                delete(ExamSubmissionModel).where(ExamSubmissionModel.exam_id.in_(exam_ids))
            )
            await db.execute(
                delete(ExamQuestionModel).where(ExamQuestionModel.exam_id.in_(exam_ids))
            )
            await db.execute(delete(ExamModel).where(ExamModel.exam_id.in_(exam_ids)))

        await db.execute(
            delete(LearnerCourseProgressModel).where(LearnerCourseProgressModel.course_id == course.course_id)
        )
        await db.execute(
            delete(QuestionModel).where(QuestionModel.course_id == course.course_id)
        )
        await db.execute(delete(CourseModel).where(CourseModel.course_id == course.course_id))

        await db.commit()
        return {"message": "deleted", "course_id": course_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while deleting course {course_id} for user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while deleting course {course_id} for user {user_id}: {str(e)}"
        )
