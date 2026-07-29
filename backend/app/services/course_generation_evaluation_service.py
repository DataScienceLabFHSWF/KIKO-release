from __future__ import annotations

import asyncio
import csv
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml

from .course_generation_config import (
    get_course_generation_count_defaults,
    validate_course_generation_counts,
)
from .course_markdown_parser_service import parse_course_markdown


COURSE_GENERATION_COUNT_DEFAULTS = get_course_generation_count_defaults()

EN_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "for", "from", "has", "have", "if", "in", "into", "is", "it", "its",
    "of", "on", "or", "that", "the", "their", "there", "these", "this", "to",
    "was", "were", "which", "with", "within", "without", "you", "your",
}

DE_STOPWORDS = {
    "aber", "als", "am", "an", "auch", "auf", "aus", "bei", "bis", "das",
    "dass", "dem", "den", "der", "des", "die", "dies", "diese", "dieser",
    "doch", "durch", "ein", "eine", "einem", "einen", "einer", "eines", "er",
    "es", "für", "hat", "ich", "im", "in", "ist", "mit", "nach", "nicht",
    "oder", "sein", "sie", "sind", "so", "und", "von", "war", "wie", "wir",
    "zu", "zum", "zur",
}

_SENTENCE_TRANSFORMER_MODEL_NAME = os.getenv(
    "COURSE_EVAL_SENTENCE_TRANSFORMER_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
_TRANSLATION_MODEL_MAP = {
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
}
_SENTENCE_TRANSFORMER_CACHE: dict[str, Any] = {}
_TRANSLATION_MODEL_CACHE: dict[tuple[str, str], tuple[Any, Any]] = {}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _average(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _tokenize(text: str) -> list[str]:
    normalized = _normalize_whitespace(text).lower()
    return re.findall(r"\b[\w-]+\b", normalized, flags=re.UNICODE)


def _detect_language_en_de(text: str) -> str:
    tokens = _tokenize(text)
    if not tokens:
        return "unknown"

    sample = tokens[:400]
    en_hits = sum(1 for token in sample if token in EN_STOPWORDS)
    de_hits = sum(1 for token in sample if token in DE_STOPWORDS)

    if en_hits == 0 and de_hits == 0:
        return "unknown"
    if en_hits >= de_hits * 1.2:
        return "en"
    if de_hits >= en_hits * 1.2:
        return "de"
    return "en" if en_hits >= de_hits else "de"


def _sentence_split(text: str) -> list[str]:
    cleaned = str(text or "").strip()
    if not cleaned:
        return []

    parts = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def _text_windows(text: str, max_sentences: int = 2) -> list[str]:
    sentences = _sentence_split(text)
    if not sentences:
        cleaned = _normalize_whitespace(text)
        return [cleaned] if cleaned else []

    windows: list[str] = []
    for size in range(1, max_sentences + 1):
        for start in range(0, len(sentences) - size + 1):
            windows.append(" ".join(sentences[start:start + size]).strip())
    return windows or [" ".join(sentences)]


def _lcs_length(left: Sequence[str], right: Sequence[str]) -> int:
    if not left or not right:
        return 0

    previous = [0] * (len(right) + 1)
    for left_token in left:
        current = [0]
        for idx, right_token in enumerate(right, start=1):
            if left_token == right_token:
                current.append(previous[idx - 1] + 1)
            else:
                current.append(max(previous[idx], current[-1]))
        previous = current
    return previous[-1]


def _token_f1(reference_text: str, candidate_text: str) -> float:
    reference_tokens = _tokenize(reference_text)
    candidate_tokens = _tokenize(candidate_text)
    if not reference_tokens or not candidate_tokens:
        return 0.0

    reference_counts = Counter(reference_tokens)
    candidate_counts = Counter(candidate_tokens)
    overlap = sum(min(reference_counts[token], candidate_counts[token]) for token in reference_counts)
    if overlap <= 0:
        return 0.0

    precision = overlap / len(candidate_tokens)
    recall = overlap / len(reference_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _rouge_l(reference_text: str, candidate_text: str) -> dict[str, float]:
    reference_tokens = _tokenize(reference_text)
    candidate_tokens = _tokenize(candidate_text)
    if not reference_tokens or not candidate_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    lcs = _lcs_length(reference_tokens, candidate_tokens)
    precision = lcs / len(candidate_tokens)
    recall = lcs / len(reference_tokens)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _pairwise_diversity(texts: Sequence[str]) -> float:
    normalized = [_normalize_whitespace(text) for text in texts if _normalize_whitespace(text)]
    if len(normalized) <= 1:
        return 1.0 if normalized else 0.0

    similarities: list[float] = []
    for idx, left in enumerate(normalized):
        for right in normalized[idx + 1:]:
            similarities.append(_token_f1(left, right))
    return _clamp01(1.0 - _average(similarities))


def _best_match_score(text: str, candidates: Sequence[str], scorer: Callable[[str, str], float]) -> float:
    cleaned = _normalize_whitespace(text)
    if not cleaned or not candidates:
        return 0.0
    return max((scorer(candidate, cleaned) for candidate in candidates), default=0.0)


def _best_match_index(text: str, candidates: Sequence[str], scorer: Callable[[str, str], float]) -> tuple[int | None, float]:
    cleaned = _normalize_whitespace(text)
    if not cleaned or not candidates:
        return None, 0.0

    best_index: int | None = None
    best_score = 0.0
    for idx, candidate in enumerate(candidates):
        score = scorer(candidate, cleaned)
        if score > best_score:
            best_score = score
            best_index = idx
    return best_index, best_score


def _extract_keywords(text: str, language: str, max_keywords: int = 20) -> list[str]:
    stopwords = DE_STOPWORDS if language == "de" else EN_STOPWORDS
    counts: Counter[str] = Counter()
    for token in _tokenize(text):
        if len(token) < 4:
            continue
        if token in stopwords:
            continue
        counts[token] += 1
    return [token for token, _ in counts.most_common(max_keywords)]


def _keyword_recall(reference_text: str, candidate_text: str, language: str, max_keywords: int = 20) -> float:
    keywords = _extract_keywords(reference_text, language=language, max_keywords=max_keywords)
    if not keywords:
        return 0.0
    candidate_tokens = set(_tokenize(candidate_text))
    hits = sum(1 for keyword in keywords if keyword in candidate_tokens)
    return hits / len(keywords)


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(float(left_value) * float(right_value) for left_value, right_value in zip(left, right))
    left_norm = sum(float(left_value) ** 2 for left_value in left) ** 0.5
    right_norm = sum(float(right_value) ** 2 for right_value in right) ** 0.5
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def _get_sentence_transformer_model() -> Any | None:
    model_name = _SENTENCE_TRANSFORMER_MODEL_NAME
    if model_name in _SENTENCE_TRANSFORMER_CACHE:
        return _SENTENCE_TRANSFORMER_CACHE[model_name]

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        _SENTENCE_TRANSFORMER_CACHE[model_name] = model
        return model
    except Exception:
        _SENTENCE_TRANSFORMER_CACHE[model_name] = None
        return None


def _encode_texts_multilingual(texts: Sequence[str]) -> list[list[float]] | None:
    model = _get_sentence_transformer_model()
    if model is None:
        return None

    cleaned_texts = [_normalize_whitespace(text) for text in texts if _normalize_whitespace(text)]
    if not cleaned_texts:
        return None

    try:
        embeddings = model.encode(
            cleaned_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [list(map(float, embedding)) for embedding in embeddings]
    except Exception:
        return None


def _get_translation_components(source_language: str, target_language: str) -> tuple[Any, Any] | None:
    key = (source_language, target_language)
    if key in _TRANSLATION_MODEL_CACHE:
        return _TRANSLATION_MODEL_CACHE[key]

    model_name = _TRANSLATION_MODEL_MAP.get(key)
    if not model_name:
        _TRANSLATION_MODEL_CACHE[key] = None
        return None

    try:
        import torch
        from transformers import MarianMTModel, MarianTokenizer

        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        if torch.cuda.is_available():
            model = model.to("cuda")

        _TRANSLATION_MODEL_CACHE[key] = (tokenizer, model)
        return _TRANSLATION_MODEL_CACHE[key]
    except Exception:
        _TRANSLATION_MODEL_CACHE[key] = None
        return None


def _translate_text_between_en_de(text: str, source_language: str, target_language: str) -> str | None:
    if not text or source_language == target_language:
        return _normalize_whitespace(text)

    translation_components = _get_translation_components(source_language, target_language)
    if translation_components is None:
        return None

    try:
        import torch

        tokenizer, model = translation_components
        chunks = [text[index:index + 500] for index in range(0, len(text), 500)] or [text]
        translated_chunks: list[str] = []

        for chunk in chunks:
            normalized_chunk = _normalize_whitespace(chunk)
            if not normalized_chunk:
                continue
            inputs = tokenizer(
                [normalized_chunk],
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            if torch.cuda.is_available():
                inputs = {key: value.to("cuda") for key, value in inputs.items()}

            with torch.no_grad():
                translated_ids = model.generate(**inputs)
            translated_text = tokenizer.batch_decode(
                translated_ids,
                skip_special_tokens=True,
            )[0]
            translated_chunks.append(_normalize_whitespace(translated_text))

        translated = " ".join(chunk for chunk in translated_chunks if chunk).strip()
        return translated or None
    except Exception:
        return None


def _semantic_grounding_via_embeddings(
    source_text: str,
    generated_summary: str,
) -> float | None:
    summary_sentences = _sentence_split(generated_summary)
    source_windows = _text_windows(source_text, max_sentences=2)
    if not summary_sentences or not source_windows:
        return None

    summary_embeddings = _encode_texts_multilingual(summary_sentences)
    source_embeddings = _encode_texts_multilingual(source_windows)
    if not summary_embeddings or not source_embeddings:
        return None

    similarities: list[float] = []
    for summary_embedding in summary_embeddings:
        best_similarity = max(
            (_cosine_similarity(summary_embedding, source_embedding) for source_embedding in source_embeddings),
            default=0.0,
        )
        similarities.append(_clamp01(best_similarity))

    return _average(similarities)


def _semantic_reference_similarity_via_embeddings(
    reference_summary: str,
    generated_summary: str,
) -> float | None:
    embeddings = _encode_texts_multilingual([reference_summary, generated_summary])
    if not embeddings or len(embeddings) != 2:
        return None
    return _clamp01(_cosine_similarity(embeddings[0], embeddings[1]))


def _semantic_best_match_scores(
    texts: Sequence[str],
    candidates: Sequence[str],
) -> list[float] | None:
    cleaned_texts = [_normalize_whitespace(text) for text in texts]
    cleaned_candidates = [
        _normalize_whitespace(candidate)
        for candidate in candidates
        if _normalize_whitespace(candidate)
    ]
    indexed_texts = [
        (idx, text)
        for idx, text in enumerate(cleaned_texts)
        if text
    ]
    if not indexed_texts or not cleaned_candidates:
        return None

    encoded_inputs = [text for _, text in indexed_texts] + cleaned_candidates
    embeddings = _encode_texts_multilingual(encoded_inputs)
    if not embeddings or len(embeddings) != len(encoded_inputs):
        return None

    text_embeddings = embeddings[:len(indexed_texts)]
    candidate_embeddings = embeddings[len(indexed_texts):]
    scores = [0.0] * len(cleaned_texts)
    for (idx, _), text_embedding in zip(indexed_texts, text_embeddings):
        scores[idx] = _clamp01(
            max(
                (
                    _cosine_similarity(text_embedding, candidate_embedding)
                    for candidate_embedding in candidate_embeddings
                ),
                default=0.0,
            )
        )
    return scores


def _semantic_pair_scores(
    left_texts: Sequence[str],
    right_texts: Sequence[str],
) -> list[float] | None:
    pairs = [
        (idx, _normalize_whitespace(left), _normalize_whitespace(right))
        for idx, (left, right) in enumerate(zip(left_texts, right_texts))
    ]
    nonempty_pairs = [
        pair
        for pair in pairs
        if pair[1] and pair[2]
    ]
    if not nonempty_pairs:
        return None

    left_inputs = [left for _, left, _ in nonempty_pairs]
    right_inputs = [right for _, _, right in nonempty_pairs]
    embeddings = _encode_texts_multilingual(left_inputs + right_inputs)
    if not embeddings or len(embeddings) != len(left_inputs) + len(right_inputs):
        return None

    left_embeddings = embeddings[:len(left_inputs)]
    right_embeddings = embeddings[len(left_inputs):]
    scores = [0.0] * len(pairs)
    for (idx, _, _), left_embedding, right_embedding in zip(
        nonempty_pairs,
        left_embeddings,
        right_embeddings,
    ):
        scores[idx] = _clamp01(_cosine_similarity(left_embedding, right_embedding))
    return scores


def _semantic_greedy_alignment(
    generated_items: Sequence[dict[str, Any]],
    reference_items: Sequence[dict[str, Any]],
    generated_text_getter: Callable[[dict[str, Any]], str],
    reference_text_getter: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]] | None:
    if not generated_items or not reference_items:
        return []

    generated_texts = [
        _normalize_whitespace(generated_text_getter(item))
        for item in generated_items
    ]
    reference_texts = [
        _normalize_whitespace(reference_text_getter(item))
        for item in reference_items
    ]
    nonempty_generated = [
        (idx, text)
        for idx, text in enumerate(generated_texts)
        if text
    ]
    nonempty_reference = [
        (idx, text)
        for idx, text in enumerate(reference_texts)
        if text
    ]
    if not nonempty_generated or not nonempty_reference:
        return []

    encoded_inputs = (
        [text for _, text in nonempty_generated]
        + [text for _, text in nonempty_reference]
    )
    embeddings = _encode_texts_multilingual(encoded_inputs)
    if not embeddings or len(embeddings) != len(encoded_inputs):
        return None

    generated_embeddings = embeddings[:len(nonempty_generated)]
    reference_embeddings = embeddings[len(nonempty_generated):]
    generated_embedding_by_index = {
        item_index: embedding
        for (item_index, _), embedding in zip(nonempty_generated, generated_embeddings)
    }
    reference_embedding_by_index = {
        item_index: embedding
        for (item_index, _), embedding in zip(nonempty_reference, reference_embeddings)
    }

    remaining = set(reference_embedding_by_index)
    matches: list[dict[str, Any]] = []
    for generated_index, generated_item in enumerate(generated_items):
        generated_embedding = generated_embedding_by_index.get(generated_index)
        if generated_embedding is None:
            continue

        best_reference_index: int | None = None
        best_score = 0.0
        for reference_index in remaining:
            score = _clamp01(
                _cosine_similarity(
                    generated_embedding,
                    reference_embedding_by_index[reference_index],
                )
            )
            if score > best_score:
                best_score = score
                best_reference_index = reference_index

        if best_reference_index is None:
            continue

        remaining.remove(best_reference_index)
        matches.append(
            {
                "generated_index": generated_index,
                "reference_index": best_reference_index,
                "score": best_score,
                "generated_item": generated_item,
                "reference_item": reference_items[best_reference_index],
            }
        )

    return matches


def _translation_rescued_summary_metrics(
    source_text: str,
    generated_summary: str,
    source_language: str,
    summary_language: str,
) -> dict[str, float | None]:
    translated_source = _translate_text_between_en_de(
        source_text,
        source_language=source_language,
        target_language=summary_language,
    )
    if not translated_source:
        return {
            "translated_source_grounding_avg": None,
            "translated_source_keyword_recall": None,
        }

    summary_sentences = _sentence_split(generated_summary)
    source_windows = _text_windows(translated_source, max_sentences=2)
    grounding_scores = [
        _best_match_score(sentence, source_windows, _token_f1)
        for sentence in summary_sentences
    ]
    return {
        "translated_source_grounding_avg": _average(grounding_scores),
        "translated_source_keyword_recall": _keyword_recall(
            translated_source,
            generated_summary,
            summary_language,
        ),
    }


def _normalize_qas(raw_questions: Any) -> list[dict[str, str]]:
    payload = raw_questions
    if isinstance(payload, dict):
        payload = payload.get("qa_list")

    if not isinstance(payload, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        question = _normalize_whitespace(item.get("question") or item.get("prompt") or "")
        answer = _normalize_whitespace(item.get("answer") or item.get("reference_answer") or "")
        normalized.append({"question": question, "answer": answer})
    return normalized


def _normalize_misconceptions(raw_misconceptions: Any) -> list[dict[str, str]]:
    payload = raw_misconceptions
    if isinstance(payload, dict):
        payload = payload.get("misconceptions") or payload.get("items")

    if not isinstance(payload, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        misconception = _normalize_whitespace(item.get("misconception") or "")
        correction = _normalize_whitespace(item.get("correction") or "")
        normalized.append(
            {
                "misconception": misconception,
                "correction": correction,
            }
        )
    return normalized


def _extract_qas_from_course_json(course_json: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    questions: list[dict[str, str]] = []
    for module in course_json.get("modules") or []:
        if not isinstance(module, dict):
            continue
        for question in module.get("questions") or []:
            if not isinstance(question, dict):
                continue
            prompt = _normalize_whitespace(question.get("prompt") or question.get("question") or "")
            answer = _normalize_whitespace(
                question.get("reference_answer") or question.get("answer") or ""
            )
            questions.append({"question": prompt, "answer": answer})
    return {"qa_list": questions}


def _extract_misconceptions_from_course_json(course_json: dict[str, Any]) -> list[dict[str, str]]:
    misconceptions: list[dict[str, str]] = []
    for module in course_json.get("modules") or []:
        if not isinstance(module, dict):
            continue
        misconceptions.extend(_normalize_misconceptions(module.get("misconceptions")))
    return misconceptions


def _normalize_course_payload(course_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(course_payload, dict):
        raise ValueError("course_payload must be a JSON object")

    course_json = course_payload.get("course_json")
    if not isinstance(course_json, dict):
        course_json = course_payload

    questions = course_payload.get("questions")
    if not questions and isinstance(course_json, dict):
        questions = _extract_qas_from_course_json(course_json)

    quiz = course_payload.get("quiz")
    if quiz is None and isinstance(course_json, dict):
        quiz = course_json.get("final_quiz")

    misconceptions = course_payload.get("misconceptions")
    if misconceptions is None and isinstance(course_json, dict):
        misconceptions = _extract_misconceptions_from_course_json(course_json)

    return {
        "summary": _normalize_whitespace(
            course_payload.get("summary")
            or course_payload.get("overview_md")
            or course_json.get("overview_md")
            or ""
        ),
        "questions": questions or {"qa_list": []},
        "quiz": quiz,
        "misconceptions": misconceptions or [],
    }


def _normalize_quiz(raw_quiz: Any) -> dict[str, Any] | None:
    if raw_quiz is None:
        return None

    if isinstance(raw_quiz, str):
        stripped = raw_quiz.strip()
        if not stripped:
            return None
        parsed = yaml.safe_load(stripped)
        return parsed if isinstance(parsed, dict) else None

    return raw_quiz if isinstance(raw_quiz, dict) else None


def _quiz_items(raw_quiz: Any) -> list[dict[str, Any]]:
    quiz = _normalize_quiz(raw_quiz)
    if not quiz:
        return []

    items = quiz.get("items")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _extract_correct_response_text(item: dict[str, Any]) -> str:
    item_type = str(item.get("type") or "").strip().lower()
    if item_type == "mcq":
        choices = item.get("choices")
        if not isinstance(choices, list):
            return ""
        for choice in choices:
            if isinstance(choice, dict) and choice.get("correct") is True:
                return _normalize_whitespace(choice.get("text") or "")
        return ""

    answer = item.get("answer")
    if isinstance(answer, bool):
        return "true" if answer else "false"
    return _normalize_whitespace(answer or "")


def _mcq_choice_texts(item: dict[str, Any]) -> list[str]:
    choices = item.get("choices")
    if not isinstance(choices, list):
        return []
    return [
        _normalize_whitespace(choice.get("text") or "")
        for choice in choices
        if isinstance(choice, dict)
    ]


def _single_correct_choice(item: dict[str, Any]) -> bool:
    item_type = str(item.get("type") or "").strip().lower()
    if item_type != "mcq":
        return bool(item.get("answer") in (True, False))

    choices = item.get("choices")
    if not isinstance(choices, list):
        return False
    correct_count = sum(1 for choice in choices if isinstance(choice, dict) and choice.get("correct") is True)
    return correct_count == 1


def _option_count_ok(item: dict[str, Any], expected_option_count: int | None) -> bool:
    if expected_option_count is None:
        return True
    item_type = str(item.get("type") or "").strip().lower()
    if item_type != "mcq":
        return False
    choices = item.get("choices")
    return isinstance(choices, list) and len(choices) == expected_option_count


def _distractor_uniqueness(item: dict[str, Any]) -> float:
    item_type = str(item.get("type") or "").strip().lower()
    if item_type != "mcq":
        return 1.0

    correct_text = _extract_correct_response_text(item)
    choice_texts = _mcq_choice_texts(item)
    distractors = [text for text in choice_texts if text and text != correct_text]
    if not distractors or not correct_text:
        return 0.0

    similarities = [_token_f1(correct_text, distractor) for distractor in distractors]
    return _clamp01(1.0 - _average(similarities))


def _greedy_alignment(
    generated_items: Sequence[dict[str, Any]],
    reference_items: Sequence[dict[str, Any]],
    generated_text_getter: Callable[[dict[str, Any]], str],
    reference_text_getter: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    if not generated_items or not reference_items:
        return []

    remaining = set(range(len(reference_items)))
    matches: list[dict[str, Any]] = []

    for generated_index, generated_item in enumerate(generated_items):
        generated_text = generated_text_getter(generated_item)
        best_reference_index: int | None = None
        best_score = 0.0

        for reference_index in remaining:
            reference_text = reference_text_getter(reference_items[reference_index])
            score = _token_f1(reference_text, generated_text)
            if score > best_score:
                best_score = score
                best_reference_index = reference_index

        if best_reference_index is None:
            continue

        remaining.remove(best_reference_index)
        matches.append(
            {
                "generated_index": generated_index,
                "reference_index": best_reference_index,
                "score": best_score,
                "generated_item": generated_item,
                "reference_item": reference_items[best_reference_index],
            }
        )

    return matches


def _load_markdown_text(path: str | os.PathLike[str]) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_pdf_text(pdf_path: str | os.PathLike[str]) -> str:
    try:
        import fitz

        pages: list[str] = []
        with fitz.open(str(pdf_path)) as document:
            for page in document:
                pages.append(page.get_text("text"))
        return "\n".join(page for page in pages if page).strip()
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            try:
                result = subprocess.run(
                    ["pdftotext", "-layout", "-nopgbrk", str(pdf_path), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip()
            except Exception as subprocess_exc:
                raise ImportError(
                    "PDF extraction requires 'fitz' (PyMuPDF), 'pypdf', or the 'pdftotext' binary."
                ) from subprocess_exc

        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page for page in pages if page).strip()


def extract_course_artifacts_from_markdown(markdown_text: str) -> dict[str, Any]:
    parsed = parse_course_markdown(markdown_text)
    course_json = parsed.get("course_json") or {}
    return {
        "summary": _normalize_whitespace(course_json.get("overview_md") or parsed.get("summary") or ""),
        "questions": parsed.get("questions_dict") or {"qa_list": []},
        "quiz": parsed.get("quiz_dict"),
        "misconceptions": _extract_misconceptions_from_course_json(course_json),
        "metadata": parsed.get("metadata") or {},
        "course_json": course_json,
    }


def load_course_artifacts_from_markdown_path(markdown_path: str | os.PathLike[str]) -> dict[str, Any]:
    return extract_course_artifacts_from_markdown(_load_markdown_text(markdown_path))


def load_course_artifacts_from_json_path(json_path: str | os.PathLike[str]) -> dict[str, Any]:
    payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return _normalize_course_payload(payload)


class CourseGenerationEvaluator:
    def __init__(self, language: str = "en") -> None:
        self.language = "de" if language == "de" else "en"

    def _compute_summary_semantic_metrics(
        self,
        source_text: str,
        generated_summary: str,
        reference_summary: str,
        source_language: str,
        summary_language: str,
    ) -> dict[str, Any]:
        semantic_source_grounding = _semantic_grounding_via_embeddings(
            source_text=source_text,
            generated_summary=generated_summary,
        )
        semantic_reference_similarity = None
        if reference_summary:
            semantic_reference_similarity = _semantic_reference_similarity_via_embeddings(
                reference_summary=reference_summary,
                generated_summary=generated_summary,
            )

        if semantic_source_grounding is not None:
            return {
                "semantic_mode": "multilingual_sentence_transformer",
                "semantic_source_grounding_avg": semantic_source_grounding,
                "semantic_reference_similarity": semantic_reference_similarity,
                "translated_source_grounding_avg": None,
                "translated_source_keyword_recall": None,
            }

        if (
            source_language in {"en", "de"}
            and summary_language in {"en", "de"}
            and source_language != summary_language
        ):
            translated_metrics = _translation_rescued_summary_metrics(
                source_text=source_text,
                generated_summary=generated_summary,
                source_language=source_language,
                summary_language=summary_language,
            )
            if translated_metrics["translated_source_grounding_avg"] is not None:
                return {
                    "semantic_mode": "translation_lexical",
                    "semantic_source_grounding_avg": None,
                    "semantic_reference_similarity": semantic_reference_similarity,
                    "translated_source_grounding_avg": translated_metrics["translated_source_grounding_avg"],
                    "translated_source_keyword_recall": translated_metrics["translated_source_keyword_recall"],
                }

        return {
            "semantic_mode": "lexical_fallback",
            "semantic_source_grounding_avg": None,
            "semantic_reference_similarity": semantic_reference_similarity,
            "translated_source_grounding_avg": None,
            "translated_source_keyword_recall": None,
        }

    def evaluate_summary(
        self,
        source_text: str,
        generated_summary: str,
        reference_summary: str | None = None,
    ) -> dict[str, Any]:
        generated_summary = _normalize_whitespace(generated_summary)
        reference_summary = _normalize_whitespace(reference_summary or "")
        source_text = _normalize_whitespace(source_text)
        source_language = _detect_language_en_de(source_text)
        summary_language = _detect_language_en_de(generated_summary)
        reference_language = _detect_language_en_de(reference_summary) if reference_summary else None
        cross_language_source_summary = (
            source_language in {"en", "de"}
            and summary_language in {"en", "de"}
            and source_language != summary_language
        )

        summary_sentences = _sentence_split(generated_summary)
        source_windows = _text_windows(source_text, max_sentences=2)
        grounding_scores = [
            _best_match_score(sentence, source_windows, _token_f1)
            for sentence in summary_sentences
        ]
        source_grounding = _average(grounding_scores)
        source_keyword_recall = _keyword_recall(
            source_text,
            generated_summary,
            source_language if source_language != "unknown" else self.language,
        )
        compression_ratio = (
            len(_tokenize(generated_summary)) / len(_tokenize(source_text))
            if _tokenize(source_text)
            else 0.0
        )

        rouge_l = {"precision": None, "recall": None, "f1": None}
        reference_token_f1 = None
        reference_keyword_recall = None

        if reference_summary:
            rouge_l_raw = _rouge_l(reference_summary, generated_summary)
            rouge_l = {key: round(value, 4) for key, value in rouge_l_raw.items()}
            reference_token_f1 = round(_token_f1(reference_summary, generated_summary), 4)
            reference_keyword_recall = round(
                _keyword_recall(
                    reference_summary,
                    generated_summary,
                    reference_language if reference_language not in (None, "unknown") else self.language,
                ),
                4,
            )
            lexical_score = _clamp01(
                0.5 * rouge_l_raw["f1"]
                + 0.25 * source_grounding
                + 0.15 * (reference_keyword_recall or 0.0)
                + 0.10 * (reference_token_f1 or 0.0)
            )
        else:
            lexical_score = _clamp01(0.65 * source_grounding + 0.35 * source_keyword_recall)

        semantic_metrics = self._compute_summary_semantic_metrics(
            source_text=source_text,
            generated_summary=generated_summary,
            reference_summary=reference_summary,
            source_language=source_language,
            summary_language=summary_language,
        )
        semantic_mode = semantic_metrics["semantic_mode"]
        semantic_source_grounding = semantic_metrics["semantic_source_grounding_avg"]
        semantic_reference_similarity = semantic_metrics["semantic_reference_similarity"]
        translated_source_grounding = semantic_metrics["translated_source_grounding_avg"]
        translated_source_keyword_recall = semantic_metrics["translated_source_keyword_recall"]

        semantic_score = None
        if semantic_mode == "multilingual_sentence_transformer":
            if reference_summary and semantic_reference_similarity is not None:
                semantic_score = _clamp01(
                    0.60 * semantic_reference_similarity
                    + 0.40 * (semantic_source_grounding or 0.0)
                )
            else:
                semantic_score = _clamp01(semantic_source_grounding or 0.0)
        elif semantic_mode == "translation_lexical":
            translation_core = _clamp01(
                0.70 * (translated_source_grounding or 0.0)
                + 0.30 * (translated_source_keyword_recall or 0.0)
            )
            if reference_summary and semantic_reference_similarity is not None:
                semantic_score = _clamp01(
                    0.65 * translation_core + 0.35 * semantic_reference_similarity
                )
            else:
                semantic_score = translation_core

        if semantic_score is None:
            score = lexical_score
        elif cross_language_source_summary:
            score = _clamp01(0.15 * lexical_score + 0.85 * semantic_score)
        else:
            score = _clamp01(0.30 * lexical_score + 0.70 * semantic_score)

        return {
            "score": round(score, 4),
            "lexical_score": round(lexical_score, 4),
            "semantic_score": round(semantic_score, 4) if semantic_score is not None else None,
            "semantic_mode": semantic_mode,
            "source_language": source_language,
            "summary_language": summary_language,
            "reference_language": reference_language,
            "cross_language_source_summary": cross_language_source_summary,
            "summary_word_count": len(_tokenize(generated_summary)),
            "source_word_count": len(_tokenize(source_text)),
            "compression_ratio": round(compression_ratio, 4),
            "source_grounding_avg": round(source_grounding, 4),
            "source_keyword_recall": round(source_keyword_recall, 4),
            "semantic_source_grounding_avg": round(semantic_source_grounding, 4)
            if semantic_source_grounding is not None
            else None,
            "semantic_reference_similarity": round(semantic_reference_similarity, 4)
            if semantic_reference_similarity is not None
            else None,
            "translated_source_grounding_avg": round(translated_source_grounding, 4)
            if translated_source_grounding is not None
            else None,
            "translated_source_keyword_recall": round(translated_source_keyword_recall, 4)
            if translated_source_keyword_recall is not None
            else None,
            "reference_rouge_l": rouge_l,
            "reference_token_f1": reference_token_f1,
            "reference_keyword_recall": reference_keyword_recall,
        }

    def evaluate_qas(
        self,
        generated_summary: str,
        generated_questions: Any,
        reference_questions: Any = None,
        expected_qa_count: int | None = None,
    ) -> dict[str, Any]:
        generated_qas = _normalize_qas(generated_questions)
        reference_qas = _normalize_qas(reference_questions)
        summary_windows = _text_windows(generated_summary, max_sentences=2)

        nonempty_flags: list[float] = []
        answer_grounding_scores: list[float] = []
        pair_grounding_scores: list[float] = []
        question_texts: list[str] = []
        answer_texts: list[str] = []
        pair_texts: list[str] = []
        items: list[dict[str, Any]] = []

        for qa in generated_qas:
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            pair_text = f"{question} {answer}".strip()
            nonempty = float(bool(question and answer))
            answer_grounding = _best_match_score(answer, summary_windows, _token_f1)
            pair_grounding = _best_match_score(pair_text, summary_windows, _token_f1)

            nonempty_flags.append(nonempty)
            answer_grounding_scores.append(answer_grounding)
            pair_grounding_scores.append(pair_grounding)
            question_texts.append(question)
            answer_texts.append(answer)
            pair_texts.append(pair_text)
            items.append(
                {
                    "question": question,
                    "answer": answer,
                    "nonempty": bool(nonempty),
                    "answer_grounding": round(answer_grounding, 4),
                    "pair_grounding": round(pair_grounding, 4),
                }
            )

        count_score = 1.0
        if expected_qa_count is not None:
            count_score = 1.0 if len(generated_qas) == expected_qa_count else 0.0

        nonempty_ratio = _average(nonempty_flags)
        answer_grounding_avg = _average(answer_grounding_scores)
        pair_grounding_avg = _average(pair_grounding_scores)
        diversity = _pairwise_diversity(question_texts)
        semantic_answer_grounding_scores = _semantic_best_match_scores(answer_texts, summary_windows)
        semantic_pair_grounding_scores = _semantic_best_match_scores(pair_texts, summary_windows)
        semantic_answer_grounding_avg = (
            _average(semantic_answer_grounding_scores)
            if semantic_answer_grounding_scores is not None
            else None
        )
        semantic_pair_grounding_avg = (
            _average(semantic_pair_grounding_scores)
            if semantic_pair_grounding_scores is not None
            else None
        )
        semantic_mode = (
            "multilingual_sentence_transformer"
            if (
                semantic_answer_grounding_scores is not None
                or semantic_pair_grounding_scores is not None
            )
            else "lexical_fallback"
        )

        if semantic_answer_grounding_scores is not None:
            for item, score in zip(items, semantic_answer_grounding_scores):
                item["semantic_answer_grounding"] = round(score, 4)
        if semantic_pair_grounding_scores is not None:
            for item, score in zip(items, semantic_pair_grounding_scores):
                item["semantic_pair_grounding"] = round(score, 4)

        blended_answer_grounding = (
            _clamp01(0.30 * answer_grounding_avg + 0.70 * semantic_answer_grounding_avg)
            if semantic_answer_grounding_avg is not None
            else answer_grounding_avg
        )
        blended_pair_grounding = (
            _clamp01(0.30 * pair_grounding_avg + 0.70 * semantic_pair_grounding_avg)
            if semantic_pair_grounding_avg is not None
            else pair_grounding_avg
        )

        reference_question_alignment = None
        reference_answer_alignment = None
        semantic_reference_question_alignment = None
        semantic_reference_answer_alignment = None
        if reference_qas:
            matches = _greedy_alignment(
                generated_items=generated_qas,
                reference_items=reference_qas,
                generated_text_getter=lambda item: item.get("question", ""),
                reference_text_getter=lambda item: item.get("question", ""),
            )
            question_scores = [match["score"] for match in matches]
            answer_scores = [
                _token_f1(
                    match["reference_item"].get("answer", ""),
                    match["generated_item"].get("answer", ""),
                )
                for match in matches
            ]
            reference_question_alignment = round(_average(question_scores), 4)
            reference_answer_alignment = round(_average(answer_scores), 4)
            lexical_reference_alignment_score = _average(question_scores + answer_scores)

            semantic_matches = _semantic_greedy_alignment(
                generated_items=generated_qas,
                reference_items=reference_qas,
                generated_text_getter=lambda item: item.get("question", ""),
                reference_text_getter=lambda item: item.get("question", ""),
            )
            semantic_reference_alignment_score = None
            if semantic_matches is not None:
                semantic_question_scores = [match["score"] for match in semantic_matches]
                semantic_answer_scores = _semantic_pair_scores(
                    [
                        match["reference_item"].get("answer", "")
                        for match in semantic_matches
                    ],
                    [
                        match["generated_item"].get("answer", "")
                        for match in semantic_matches
                    ],
                )
                semantic_reference_question_alignment = round(
                    _average(semantic_question_scores),
                    4,
                )
                if semantic_answer_scores is not None:
                    semantic_reference_answer_alignment = round(
                        _average(semantic_answer_scores),
                        4,
                    )
                    semantic_reference_alignment_score = _average(
                        semantic_question_scores + semantic_answer_scores
                    )
                else:
                    semantic_reference_alignment_score = _average(semantic_question_scores)

            reference_alignment_score = (
                _clamp01(
                    0.30 * lexical_reference_alignment_score
                    + 0.70 * semantic_reference_alignment_score
                )
                if semantic_reference_alignment_score is not None
                else lexical_reference_alignment_score
            )
            score = _clamp01(
                0.15 * count_score
                + 0.15 * nonempty_ratio
                + 0.20 * blended_answer_grounding
                + 0.15 * blended_pair_grounding
                + 0.15 * diversity
                + 0.20 * reference_alignment_score
            )
        else:
            score = _clamp01(
                0.20 * count_score
                + 0.20 * nonempty_ratio
                + 0.30 * blended_answer_grounding
                + 0.15 * blended_pair_grounding
                + 0.15 * diversity
            )

        return {
            "score": round(score, 4),
            "count": len(generated_qas),
            "expected_count": expected_qa_count,
            "count_match": bool(expected_qa_count is None or len(generated_qas) == expected_qa_count),
            "nonempty_ratio": round(nonempty_ratio, 4),
            "answer_grounding_avg": round(answer_grounding_avg, 4),
            "pair_grounding_avg": round(pair_grounding_avg, 4),
            "semantic_mode": semantic_mode,
            "semantic_answer_grounding_avg": round(semantic_answer_grounding_avg, 4)
            if semantic_answer_grounding_avg is not None
            else None,
            "semantic_pair_grounding_avg": round(semantic_pair_grounding_avg, 4)
            if semantic_pair_grounding_avg is not None
            else None,
            "blended_answer_grounding_avg": round(blended_answer_grounding, 4),
            "blended_pair_grounding_avg": round(blended_pair_grounding, 4),
            "question_diversity": round(diversity, 4),
            "reference_question_alignment_avg": reference_question_alignment,
            "reference_answer_alignment_avg": reference_answer_alignment,
            "semantic_reference_question_alignment_avg": semantic_reference_question_alignment,
            "semantic_reference_answer_alignment_avg": semantic_reference_answer_alignment,
            "items": items,
        }

    def evaluate_quiz(
        self,
        generated_summary: str,
        generated_quiz: Any,
        reference_quiz: Any = None,
        expected_question_count: int | None = None,
        expected_option_count: int | None = None,
    ) -> dict[str, Any]:
        quiz = _normalize_quiz(generated_quiz)
        items = _quiz_items(quiz)
        reference_items = _quiz_items(reference_quiz)
        summary_windows = _text_windows(generated_summary, max_sentences=2)

        if not quiz:
            return {
                "score": 0.0,
                "has_quiz": False,
                "count": 0,
                "expected_count": expected_question_count,
                "count_match": False,
                "single_correct_ratio": 0.0,
                "option_count_ratio": 0.0,
                "prompt_grounding_avg": 0.0,
                "correct_answer_grounding_avg": 0.0,
                "semantic_mode": "lexical_fallback",
                "semantic_prompt_grounding_avg": None,
                "semantic_correct_answer_grounding_avg": None,
                "blended_prompt_grounding_avg": 0.0,
                "blended_correct_answer_grounding_avg": 0.0,
                "distractor_uniqueness_avg": 0.0,
                "question_diversity": 0.0,
                "reference_prompt_alignment_avg": None,
                "reference_correct_alignment_avg": None,
                "semantic_reference_prompt_alignment_avg": None,
                "semantic_reference_correct_alignment_avg": None,
                "items": [],
                "error": "Quiz was missing or could not be parsed.",
            }

        single_correct_flags: list[float] = []
        option_count_flags: list[float] = []
        prompt_grounding_scores: list[float] = []
        correct_grounding_scores: list[float] = []
        distractor_uniqueness_scores: list[float] = []
        prompt_texts: list[str] = []
        correct_texts: list[str] = []
        item_details: list[dict[str, Any]] = []

        for item in items:
            prompt = _normalize_whitespace(item.get("prompt") or "")
            correct_response = _extract_correct_response_text(item)
            single_correct = float(_single_correct_choice(item))
            option_count_ok = float(_option_count_ok(item, expected_option_count))
            prompt_grounding = _best_match_score(prompt, summary_windows, _token_f1)
            correct_grounding = _best_match_score(correct_response, summary_windows, _token_f1)
            distractor_uniqueness = _distractor_uniqueness(item)

            single_correct_flags.append(single_correct)
            option_count_flags.append(option_count_ok)
            prompt_grounding_scores.append(prompt_grounding)
            correct_grounding_scores.append(correct_grounding)
            distractor_uniqueness_scores.append(distractor_uniqueness)
            prompt_texts.append(prompt)
            correct_texts.append(correct_response)

            item_details.append(
                {
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "prompt": prompt,
                    "single_correct": bool(single_correct),
                    "option_count_ok": bool(option_count_ok),
                    "prompt_grounding": round(prompt_grounding, 4),
                    "correct_answer_grounding": round(correct_grounding, 4),
                    "distractor_uniqueness": round(distractor_uniqueness, 4),
                }
            )

        count_match = bool(expected_question_count is None or len(items) == expected_question_count)
        count_score = 1.0 if count_match else 0.0
        single_correct_ratio = _average(single_correct_flags)
        option_count_ratio = _average(option_count_flags)
        prompt_grounding_avg = _average(prompt_grounding_scores)
        correct_grounding_avg = _average(correct_grounding_scores)
        distractor_uniqueness_avg = _average(distractor_uniqueness_scores)
        question_diversity = _pairwise_diversity(prompt_texts)
        semantic_prompt_grounding_scores = _semantic_best_match_scores(prompt_texts, summary_windows)
        semantic_correct_grounding_scores = _semantic_best_match_scores(correct_texts, summary_windows)
        semantic_prompt_grounding_avg = (
            _average(semantic_prompt_grounding_scores)
            if semantic_prompt_grounding_scores is not None
            else None
        )
        semantic_correct_grounding_avg = (
            _average(semantic_correct_grounding_scores)
            if semantic_correct_grounding_scores is not None
            else None
        )
        semantic_mode = (
            "multilingual_sentence_transformer"
            if (
                semantic_prompt_grounding_scores is not None
                or semantic_correct_grounding_scores is not None
            )
            else "lexical_fallback"
        )

        if semantic_prompt_grounding_scores is not None:
            for item_detail, score in zip(item_details, semantic_prompt_grounding_scores):
                item_detail["semantic_prompt_grounding"] = round(score, 4)
        if semantic_correct_grounding_scores is not None:
            for item_detail, score in zip(item_details, semantic_correct_grounding_scores):
                item_detail["semantic_correct_answer_grounding"] = round(score, 4)

        blended_prompt_grounding = (
            _clamp01(0.30 * prompt_grounding_avg + 0.70 * semantic_prompt_grounding_avg)
            if semantic_prompt_grounding_avg is not None
            else prompt_grounding_avg
        )
        blended_correct_grounding = (
            _clamp01(0.30 * correct_grounding_avg + 0.70 * semantic_correct_grounding_avg)
            if semantic_correct_grounding_avg is not None
            else correct_grounding_avg
        )
        structure_score = _average([count_score, single_correct_ratio, option_count_ratio])
        grounding_score = _average([blended_prompt_grounding, blended_correct_grounding])
        diversity_score = _average([distractor_uniqueness_avg, question_diversity])

        reference_prompt_alignment = None
        reference_correct_alignment = None
        semantic_reference_prompt_alignment = None
        semantic_reference_correct_alignment = None
        if reference_items:
            matches = _greedy_alignment(
                generated_items=items,
                reference_items=reference_items,
                generated_text_getter=lambda item: _normalize_whitespace(item.get("prompt") or ""),
                reference_text_getter=lambda item: _normalize_whitespace(item.get("prompt") or ""),
            )
            prompt_scores = [match["score"] for match in matches]
            compatible_answer_scores: list[float] = []
            for match in matches:
                generated_type = str(match["generated_item"].get("type") or "").strip().lower()
                reference_type = str(match["reference_item"].get("type") or "").strip().lower()
                if generated_type == reference_type:
                    compatible_answer_scores.append(
                        _token_f1(
                            _extract_correct_response_text(match["reference_item"]),
                            _extract_correct_response_text(match["generated_item"]),
                        )
                    )

            reference_prompt_alignment = round(_average(prompt_scores), 4)
            if compatible_answer_scores:
                reference_correct_alignment = round(_average(compatible_answer_scores), 4)
                lexical_reference_alignment_score = _average(prompt_scores + compatible_answer_scores)
            else:
                lexical_reference_alignment_score = _average(prompt_scores)

            semantic_matches = _semantic_greedy_alignment(
                generated_items=items,
                reference_items=reference_items,
                generated_text_getter=lambda item: _normalize_whitespace(item.get("prompt") or ""),
                reference_text_getter=lambda item: _normalize_whitespace(item.get("prompt") or ""),
            )
            semantic_reference_alignment_score = None
            if semantic_matches is not None:
                semantic_prompt_scores = [match["score"] for match in semantic_matches]
                semantic_compatible_answer_scores = _semantic_pair_scores(
                    [
                        _extract_correct_response_text(match["reference_item"])
                        for match in semantic_matches
                        if (
                            str(match["generated_item"].get("type") or "").strip().lower()
                            == str(match["reference_item"].get("type") or "").strip().lower()
                        )
                    ],
                    [
                        _extract_correct_response_text(match["generated_item"])
                        for match in semantic_matches
                        if (
                            str(match["generated_item"].get("type") or "").strip().lower()
                            == str(match["reference_item"].get("type") or "").strip().lower()
                        )
                    ],
                )
                semantic_reference_prompt_alignment = round(
                    _average(semantic_prompt_scores),
                    4,
                )
                if semantic_compatible_answer_scores is not None:
                    semantic_reference_correct_alignment = round(
                        _average(semantic_compatible_answer_scores),
                        4,
                    )
                    semantic_reference_alignment_score = _average(
                        semantic_prompt_scores + semantic_compatible_answer_scores
                    )
                else:
                    semantic_reference_alignment_score = _average(semantic_prompt_scores)

            reference_alignment_score = (
                _clamp01(
                    0.30 * lexical_reference_alignment_score
                    + 0.70 * semantic_reference_alignment_score
                )
                if semantic_reference_alignment_score is not None
                else lexical_reference_alignment_score
            )

            score = _clamp01(
                0.35 * structure_score
                + 0.20 * grounding_score
                + 0.15 * diversity_score
                + 0.30 * reference_alignment_score
            )
        else:
            score = _clamp01(0.45 * structure_score + 0.35 * grounding_score + 0.20 * diversity_score)

        return {
            "score": round(score, 4),
            "has_quiz": True,
            "count": len(items),
            "expected_count": expected_question_count,
            "count_match": count_match,
            "single_correct_ratio": round(single_correct_ratio, 4),
            "option_count_ratio": round(option_count_ratio, 4),
            "prompt_grounding_avg": round(prompt_grounding_avg, 4),
            "correct_answer_grounding_avg": round(correct_grounding_avg, 4),
            "semantic_mode": semantic_mode,
            "semantic_prompt_grounding_avg": round(semantic_prompt_grounding_avg, 4)
            if semantic_prompt_grounding_avg is not None
            else None,
            "semantic_correct_answer_grounding_avg": round(semantic_correct_grounding_avg, 4)
            if semantic_correct_grounding_avg is not None
            else None,
            "blended_prompt_grounding_avg": round(blended_prompt_grounding, 4),
            "blended_correct_answer_grounding_avg": round(blended_correct_grounding, 4),
            "distractor_uniqueness_avg": round(distractor_uniqueness_avg, 4),
            "question_diversity": round(question_diversity, 4),
            "reference_prompt_alignment_avg": reference_prompt_alignment,
            "reference_correct_alignment_avg": reference_correct_alignment,
            "semantic_reference_prompt_alignment_avg": semantic_reference_prompt_alignment,
            "semantic_reference_correct_alignment_avg": semantic_reference_correct_alignment,
            "items": item_details,
        }

    def evaluate_misconceptions(
        self,
        generated_summary: str,
        generated_misconceptions: Any,
        reference_misconceptions: Any = None,
        expected_misconception_count: int | None = None,
    ) -> dict[str, Any]:
        misconceptions = _normalize_misconceptions(generated_misconceptions)
        reference_items = _normalize_misconceptions(reference_misconceptions)
        summary_windows = _text_windows(generated_summary, max_sentences=2)

        if not misconceptions:
            return {
                "score": 0.0,
                "count": 0,
                "expected_count": expected_misconception_count,
                "count_match": False,
                "nonempty_ratio": 0.0,
                "grounding_avg": 0.0,
                "semantic_mode": "lexical_fallback",
                "semantic_grounding_avg": None,
                "blended_grounding_avg": 0.0,
                "diversity": 0.0,
                "reference_alignment_avg": None,
                "semantic_reference_alignment_avg": None,
                "items": [],
                "error": "Misconceptions were missing or could not be parsed.",
            }

        nonempty_flags: list[float] = []
        grounding_scores: list[float] = []
        misconception_texts: list[str] = []
        pair_texts: list[str] = []
        item_details: list[dict[str, Any]] = []

        for item in misconceptions:
            misconception = item.get("misconception", "")
            correction = item.get("correction", "")
            pair_text = f"{misconception} {correction}".strip()
            nonempty = float(bool(misconception and correction))
            grounding = _best_match_score(pair_text, summary_windows, _token_f1)

            nonempty_flags.append(nonempty)
            grounding_scores.append(grounding)
            misconception_texts.append(misconception)
            pair_texts.append(pair_text)
            item_details.append(
                {
                    "misconception": misconception,
                    "correction": correction,
                    "nonempty": bool(nonempty),
                    "grounding": round(grounding, 4),
                }
            )

        count_match = bool(
            expected_misconception_count is not None
            and len(misconceptions) == expected_misconception_count
        )
        count_score = (
            1.0
            if expected_misconception_count is None or count_match
            else 0.0
        )
        nonempty_ratio = _average(nonempty_flags)
        grounding_avg = _average(grounding_scores)
        diversity = _pairwise_diversity(misconception_texts)
        semantic_grounding_scores = _semantic_best_match_scores(pair_texts, summary_windows)
        semantic_grounding_avg = (
            _average(semantic_grounding_scores)
            if semantic_grounding_scores is not None
            else None
        )
        semantic_mode = (
            "multilingual_sentence_transformer"
            if semantic_grounding_scores is not None
            else "lexical_fallback"
        )
        if semantic_grounding_scores is not None:
            for item_detail, score in zip(item_details, semantic_grounding_scores):
                item_detail["semantic_grounding"] = round(score, 4)

        blended_grounding = (
            _clamp01(0.30 * grounding_avg + 0.70 * semantic_grounding_avg)
            if semantic_grounding_avg is not None
            else grounding_avg
        )

        reference_alignment = None
        semantic_reference_alignment = None
        if reference_items:
            matches = _greedy_alignment(
                generated_items=misconceptions,
                reference_items=reference_items,
                generated_text_getter=lambda item: (
                    f"{item.get('misconception', '')} {item.get('correction', '')}"
                ),
                reference_text_getter=lambda item: (
                    f"{item.get('misconception', '')} {item.get('correction', '')}"
                ),
            )
            lexical_scores = [match["score"] for match in matches]
            lexical_reference_alignment = _average(lexical_scores)
            reference_alignment = round(lexical_reference_alignment, 4)

            semantic_matches = _semantic_greedy_alignment(
                generated_items=misconceptions,
                reference_items=reference_items,
                generated_text_getter=lambda item: (
                    f"{item.get('misconception', '')} {item.get('correction', '')}"
                ),
                reference_text_getter=lambda item: (
                    f"{item.get('misconception', '')} {item.get('correction', '')}"
                ),
            )
            semantic_reference_alignment_score = None
            if semantic_matches is not None:
                semantic_scores = [match["score"] for match in semantic_matches]
                semantic_reference_alignment_score = _average(semantic_scores)
                semantic_reference_alignment = round(
                    semantic_reference_alignment_score,
                    4,
                )

            reference_alignment_score = (
                _clamp01(
                    0.30 * lexical_reference_alignment
                    + 0.70 * semantic_reference_alignment_score
                )
                if semantic_reference_alignment_score is not None
                else lexical_reference_alignment
            )
            score = _clamp01(
                0.15 * count_score
                + 0.15 * nonempty_ratio
                + 0.30 * blended_grounding
                + 0.15 * diversity
                + 0.25 * reference_alignment_score
            )
        else:
            score = _clamp01(
                0.20 * count_score
                + 0.20 * nonempty_ratio
                + 0.40 * blended_grounding
                + 0.20 * diversity
            )

        return {
            "score": round(score, 4),
            "count": len(misconceptions),
            "expected_count": expected_misconception_count,
            "count_match": bool(
                expected_misconception_count is None
                or len(misconceptions) == expected_misconception_count
            ),
            "nonempty_ratio": round(nonempty_ratio, 4),
            "grounding_avg": round(grounding_avg, 4),
            "semantic_mode": semantic_mode,
            "semantic_grounding_avg": round(semantic_grounding_avg, 4)
            if semantic_grounding_avg is not None
            else None,
            "blended_grounding_avg": round(blended_grounding, 4),
            "diversity": round(diversity, 4),
            "reference_alignment_avg": reference_alignment,
            "semantic_reference_alignment_avg": semantic_reference_alignment,
            "items": item_details,
        }

    def evaluate_course_outputs(
        self,
        source_text: str,
        generated_summary: str,
        generated_questions: Any,
        generated_quiz: Any,
        generated_misconceptions: Any = None,
        reference_summary: str | None = None,
        reference_questions: Any = None,
        reference_quiz: Any = None,
        reference_misconceptions: Any = None,
        expected_qa_count: int | None = None,
        expected_quiz_question_count: int | None = None,
        expected_quiz_option_count: int | None = None,
        expected_misconception_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        summary_report = self.evaluate_summary(
            source_text=source_text,
            generated_summary=generated_summary,
            reference_summary=reference_summary,
        )
        qa_report = self.evaluate_qas(
            generated_summary=generated_summary,
            generated_questions=generated_questions,
            reference_questions=reference_questions,
            expected_qa_count=expected_qa_count,
        )
        quiz_report = self.evaluate_quiz(
            generated_summary=generated_summary,
            generated_quiz=generated_quiz,
            reference_quiz=reference_quiz,
            expected_question_count=expected_quiz_question_count,
            expected_option_count=expected_quiz_option_count,
        )
        misconceptions_report = self.evaluate_misconceptions(
            generated_summary=generated_summary,
            generated_misconceptions=generated_misconceptions,
            reference_misconceptions=reference_misconceptions,
            expected_misconception_count=expected_misconception_count,
        )

        overall_score = _clamp01(
            0.35 * summary_report["score"]
            + 0.25 * qa_report["score"]
            + 0.25 * quiz_report["score"]
            + 0.15 * misconceptions_report["score"]
        )

        return {
            "metadata": metadata or {},
            "summary": summary_report,
            "qa": qa_report,
            "quiz": quiz_report,
            "misconceptions": misconceptions_report,
            "overall": {
                "score": round(overall_score, 4),
                "reference_available": bool(
                    reference_summary
                    or reference_questions
                    or reference_quiz
                    or reference_misconceptions
                ),
            },
        }


def flatten_course_generation_report(report: dict[str, Any]) -> dict[str, Any]:
    metadata = report.get("metadata") or {}
    summary = report.get("summary") or {}
    qa = report.get("qa") or {}
    quiz = report.get("quiz") or {}
    misconceptions = report.get("misconceptions") or {}
    overall = report.get("overall") or {}
    reference_rouge_l = summary.get("reference_rouge_l") or {}

    return {
        "source_pdf": metadata.get("source_pdf"),
        "generated_markdown_path": metadata.get("generated_markdown_path"),
        "reference_markdown_path": metadata.get("reference_markdown_path"),
        "response_language": metadata.get("response_language"),
        "llm_model_name": metadata.get("llm_model_name"),
        "processing_time_seconds": metadata.get("processing_time_seconds"),
        "generated_markdown_valid": metadata.get("generated_markdown_valid"),
        "overall_score": overall.get("score"),
        "summary_score": summary.get("score"),
        "summary_lexical_score": summary.get("lexical_score"),
        "summary_semantic_score": summary.get("semantic_score"),
        "summary_semantic_mode": summary.get("semantic_mode"),
        "summary_source_language": summary.get("source_language"),
        "summary_summary_language": summary.get("summary_language"),
        "summary_reference_language": summary.get("reference_language"),
        "summary_cross_language_source_summary": summary.get("cross_language_source_summary"),
        "summary_word_count": summary.get("summary_word_count"),
        "summary_source_grounding_avg": summary.get("source_grounding_avg"),
        "summary_source_keyword_recall": summary.get("source_keyword_recall"),
        "summary_semantic_source_grounding_avg": summary.get("semantic_source_grounding_avg"),
        "summary_semantic_reference_similarity": summary.get("semantic_reference_similarity"),
        "summary_translated_source_grounding_avg": summary.get("translated_source_grounding_avg"),
        "summary_translated_source_keyword_recall": summary.get("translated_source_keyword_recall"),
        "summary_reference_rouge_l_f1": reference_rouge_l.get("f1"),
        "qa_score": qa.get("score"),
        "qa_count": qa.get("count"),
        "qa_count_match": qa.get("count_match"),
        "qa_semantic_mode": qa.get("semantic_mode"),
        "qa_answer_grounding_avg": qa.get("answer_grounding_avg"),
        "qa_pair_grounding_avg": qa.get("pair_grounding_avg"),
        "qa_semantic_answer_grounding_avg": qa.get("semantic_answer_grounding_avg"),
        "qa_semantic_pair_grounding_avg": qa.get("semantic_pair_grounding_avg"),
        "qa_blended_answer_grounding_avg": qa.get("blended_answer_grounding_avg"),
        "qa_blended_pair_grounding_avg": qa.get("blended_pair_grounding_avg"),
        "qa_question_diversity": qa.get("question_diversity"),
        "qa_reference_question_alignment_avg": qa.get("reference_question_alignment_avg"),
        "qa_reference_answer_alignment_avg": qa.get("reference_answer_alignment_avg"),
        "qa_semantic_reference_question_alignment_avg": qa.get("semantic_reference_question_alignment_avg"),
        "qa_semantic_reference_answer_alignment_avg": qa.get("semantic_reference_answer_alignment_avg"),
        "quiz_score": quiz.get("score"),
        "quiz_has_quiz": quiz.get("has_quiz"),
        "quiz_count": quiz.get("count"),
        "quiz_count_match": quiz.get("count_match"),
        "quiz_single_correct_ratio": quiz.get("single_correct_ratio"),
        "quiz_option_count_ratio": quiz.get("option_count_ratio"),
        "quiz_semantic_mode": quiz.get("semantic_mode"),
        "quiz_prompt_grounding_avg": quiz.get("prompt_grounding_avg"),
        "quiz_correct_answer_grounding_avg": quiz.get("correct_answer_grounding_avg"),
        "quiz_semantic_prompt_grounding_avg": quiz.get("semantic_prompt_grounding_avg"),
        "quiz_semantic_correct_answer_grounding_avg": quiz.get("semantic_correct_answer_grounding_avg"),
        "quiz_blended_prompt_grounding_avg": quiz.get("blended_prompt_grounding_avg"),
        "quiz_blended_correct_answer_grounding_avg": quiz.get("blended_correct_answer_grounding_avg"),
        "quiz_distractor_uniqueness_avg": quiz.get("distractor_uniqueness_avg"),
        "quiz_question_diversity": quiz.get("question_diversity"),
        "quiz_reference_prompt_alignment_avg": quiz.get("reference_prompt_alignment_avg"),
        "quiz_reference_correct_alignment_avg": quiz.get("reference_correct_alignment_avg"),
        "quiz_semantic_reference_prompt_alignment_avg": quiz.get("semantic_reference_prompt_alignment_avg"),
        "quiz_semantic_reference_correct_alignment_avg": quiz.get("semantic_reference_correct_alignment_avg"),
        "misconceptions_score": misconceptions.get("score"),
        "misconceptions_count": misconceptions.get("count"),
        "misconceptions_count_match": misconceptions.get("count_match"),
        "misconceptions_nonempty_ratio": misconceptions.get("nonempty_ratio"),
        "misconceptions_semantic_mode": misconceptions.get("semantic_mode"),
        "misconceptions_grounding_avg": misconceptions.get("grounding_avg"),
        "misconceptions_semantic_grounding_avg": misconceptions.get("semantic_grounding_avg"),
        "misconceptions_blended_grounding_avg": misconceptions.get("blended_grounding_avg"),
        "misconceptions_diversity": misconceptions.get("diversity"),
        "misconceptions_reference_alignment_avg": misconceptions.get("reference_alignment_avg"),
        "misconceptions_semantic_reference_alignment_avg": misconceptions.get("semantic_reference_alignment_avg"),
    }


def write_flat_report_csv(report: dict[str, Any], output_path: str | os.PathLike[str]) -> None:
    flat_report = flatten_course_generation_report(report)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(flat_report.keys()))
        writer.writeheader()
        writer.writerow(flat_report)


def _ensure_local_prompt_dir(configs: dict[str, Any]) -> None:
    app_config = configs.get("app_config")
    prompt_dir = getattr(app_config, "prompt_templates_dir", None)
    if prompt_dir and os.path.isdir(prompt_dir):
        return

    local_prompt_dir = Path(__file__).resolve().parents[1] / "core" / "prompts"
    if app_config is not None:
        app_config.prompt_templates_dir = str(local_prompt_dir)


def _generated_markdown_validation(markdown_text: str) -> tuple[bool, str | None]:
    try:
        parse_course_markdown(markdown_text)
        return True, None
    except Exception as exc:
        return False, str(exc)


async def run_pdf_course_generation_benchmark(
    pdf_path: str | os.PathLike[str],
    reference_markdown_path: str | os.PathLike[str] | None = None,
    response_language: str = "en",
    llm_model_name: str | None = None,
    qa_count: int = COURSE_GENERATION_COUNT_DEFAULTS["qa_count"],
    quiz_question_count: int = COURSE_GENERATION_COUNT_DEFAULTS["quiz_question_count"],
    quiz_option_count: int = COURSE_GENERATION_COUNT_DEFAULTS["quiz_option_count"],
    misconception_count: int = COURSE_GENERATION_COUNT_DEFAULTS["misconception_count"],
) -> dict[str, Any]:
    from app.core import PromptManager
    from .configuration_service import get_app_config_and_libary_available
    from .course_creator_manager import AsyncBatchProcessor

    configs = await get_app_config_and_libary_available()
    _ensure_local_prompt_dir(configs)

    resolved_llm_model_name = llm_model_name or getattr(configs.get("app_config"), "default_llm_model", None)
    if not resolved_llm_model_name:
        raise ValueError("No llm_model_name was provided and no default_llm_model is configured.")

    counts = validate_course_generation_counts(
        qa_count=qa_count,
        quiz_question_count=quiz_question_count,
        quiz_option_count=quiz_option_count,
        misconception_count=misconception_count,
    )
    qa_count = counts["qa_count"]
    quiz_question_count = counts["quiz_question_count"]
    quiz_option_count = counts["quiz_option_count"]
    misconception_count = counts["misconception_count"]

    prompt_manager = PromptManager(configs)
    processor = AsyncBatchProcessor(
        prompt_manager=prompt_manager,
        llm_model_name=resolved_llm_model_name,
        response_language=response_language,
    )

    generated = await processor.summarize_document(
        str(pdf_path),
        qa_count=qa_count,
        quiz_question_count=quiz_question_count,
        quiz_option_count=quiz_option_count,
        misconception_count=misconception_count,
    )

    source_text = load_pdf_text(pdf_path)
    evaluator = CourseGenerationEvaluator(language=response_language)

    reference_artifacts = None
    if reference_markdown_path:
        reference_artifacts = load_course_artifacts_from_markdown_path(reference_markdown_path)

    generated_markdown = generated.get("generated_markdown") or ""
    generated_markdown_valid, generated_markdown_error = _generated_markdown_validation(generated_markdown)

    return evaluator.evaluate_course_outputs(
        source_text=source_text,
        generated_summary=generated.get("final_summary") or "",
        generated_questions=generated.get("questions") or {"qa_list": []},
        generated_quiz=generated.get("quiz"),
        generated_misconceptions=generated.get("misconceptions"),
        reference_summary=(reference_artifacts or {}).get("summary"),
        reference_questions=(reference_artifacts or {}).get("questions"),
        reference_quiz=(reference_artifacts or {}).get("quiz"),
        reference_misconceptions=(reference_artifacts or {}).get("misconceptions"),
        expected_qa_count=qa_count,
        expected_quiz_question_count=quiz_question_count,
        expected_quiz_option_count=quiz_option_count,
        expected_misconception_count=misconception_count,
        metadata={
            "source_pdf": str(pdf_path),
            "reference_markdown_path": str(reference_markdown_path) if reference_markdown_path else None,
            "response_language": response_language,
            "llm_model_name": resolved_llm_model_name,
            "processing_time_seconds": generated.get("processing_time_seconds"),
            "generated_markdown_valid": generated_markdown_valid,
            "generated_markdown_error": generated_markdown_error,
        },
    )


def evaluate_generated_course_markdown(
    pdf_path: str | os.PathLike[str],
    generated_markdown_path: str | os.PathLike[str],
    reference_markdown_path: str | os.PathLike[str] | None = None,
    response_language: str = "en",
    expected_qa_count: int | None = None,
    expected_quiz_question_count: int | None = None,
    expected_quiz_option_count: int | None = None,
    expected_misconception_count: int | None = None,
) -> dict[str, Any]:
    source_text = load_pdf_text(pdf_path)
    generated_artifacts = load_course_artifacts_from_markdown_path(generated_markdown_path)
    reference_artifacts = (
        load_course_artifacts_from_markdown_path(reference_markdown_path)
        if reference_markdown_path
        else None
    )

    evaluator = CourseGenerationEvaluator(language=response_language)
    generated_markdown_valid, generated_markdown_error = _generated_markdown_validation(
        _load_markdown_text(generated_markdown_path)
    )

    return evaluator.evaluate_course_outputs(
        source_text=source_text,
        generated_summary=generated_artifacts.get("summary") or "",
        generated_questions=generated_artifacts.get("questions") or {"qa_list": []},
        generated_quiz=generated_artifacts.get("quiz"),
        generated_misconceptions=generated_artifacts.get("misconceptions"),
        reference_summary=(reference_artifacts or {}).get("summary"),
        reference_questions=(reference_artifacts or {}).get("questions"),
        reference_quiz=(reference_artifacts or {}).get("quiz"),
        reference_misconceptions=(reference_artifacts or {}).get("misconceptions"),
        expected_qa_count=expected_qa_count,
        expected_quiz_question_count=expected_quiz_question_count,
        expected_quiz_option_count=expected_quiz_option_count,
        expected_misconception_count=expected_misconception_count,
        metadata={
            "source_pdf": str(pdf_path),
            "generated_markdown_path": str(generated_markdown_path),
            "reference_markdown_path": str(reference_markdown_path) if reference_markdown_path else None,
            "response_language": response_language,
            "generated_markdown_valid": generated_markdown_valid,
            "generated_markdown_error": generated_markdown_error,
        },
    )


def evaluate_generated_course_json(
    pdf_path: str | os.PathLike[str],
    generated_course_json_path: str | os.PathLike[str],
    reference_markdown_path: str | os.PathLike[str] | None = None,
    response_language: str = "en",
    expected_qa_count: int | None = None,
    expected_quiz_question_count: int | None = None,
    expected_quiz_option_count: int | None = None,
    expected_misconception_count: int | None = None,
) -> dict[str, Any]:
    source_text = load_pdf_text(pdf_path)
    generated_artifacts = load_course_artifacts_from_json_path(generated_course_json_path)
    reference_artifacts = (
        load_course_artifacts_from_markdown_path(reference_markdown_path)
        if reference_markdown_path
        else None
    )

    evaluator = CourseGenerationEvaluator(language=response_language)

    return evaluator.evaluate_course_outputs(
        source_text=source_text,
        generated_summary=generated_artifacts.get("summary") or "",
        generated_questions=generated_artifacts.get("questions") or {"qa_list": []},
        generated_quiz=generated_artifacts.get("quiz"),
        generated_misconceptions=generated_artifacts.get("misconceptions"),
        reference_summary=(reference_artifacts or {}).get("summary"),
        reference_questions=(reference_artifacts or {}).get("questions"),
        reference_quiz=(reference_artifacts or {}).get("quiz"),
        reference_misconceptions=(reference_artifacts or {}).get("misconceptions"),
        expected_qa_count=expected_qa_count,
        expected_quiz_question_count=expected_quiz_question_count,
        expected_quiz_option_count=expected_quiz_option_count,
        expected_misconception_count=expected_misconception_count,
        metadata={
            "source_pdf": str(pdf_path),
            "generated_course_json_path": str(generated_course_json_path),
            "reference_markdown_path": str(reference_markdown_path) if reference_markdown_path else None,
            "response_language": response_language,
        },
    )


def save_report_json(report: dict[str, Any], output_path: str | os.PathLike[str]) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
