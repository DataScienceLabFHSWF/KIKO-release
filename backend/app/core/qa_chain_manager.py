# backend/app/core/qa_chain_manager.py
import asyncio
import os, logging, torch
from typing import List
from functools import lru_cache
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_huggingface.llms import HuggingFacePipeline
from dotenv import load_dotenv
from app.utils import lang_display, get_device_and_dtype
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

logger = logging.getLogger(__name__)
load_dotenv()

DOCKER_OLLAMA_URL = os.getenv("DOCKER_OLLAMA_URL")
HUGGINGFACE_HUB_TOKEN = os.getenv("HUGGINGFACE_HUB_TOKEN")
CHAT_QUESTION_PROMPT_NAME = "chat_question_prompt"

class QAChainManager:
    """Manager for QA chains with different LLMs and prompts."""

    def __init__(
        self, 
        prompt_manager, 
        response_language: str
    ):
        """Initialize QAChainManager with prompt manager and language."""
        print("ℹ️ Initializing QAChainManager with config and prompt manager")        
        self.prompt_manager = prompt_manager
        self.response_language = response_language

    @staticmethod
    @lru_cache(maxsize=16)
    def _get_ollama_llm(model_name: str) -> OllamaLLM:
        if not DOCKER_OLLAMA_URL:
            raise ValueError("❌ DOCKER_OLLAMA_URL is not configured.")

        return OllamaLLM(
            model=model_name,
            base_url=DOCKER_OLLAMA_URL,
            temperature=0.2,
            top_k=50,
            top_p=0.8,
            repeat_penalty=1.15,
            num_predict=220,
            stop=[],
        )

    @staticmethod
    @lru_cache(maxsize=4)
    def _get_hf_llm(
        model_name: str, 
        quant: str | None = None
    ) -> HuggingFacePipeline:
        if not HUGGINGFACE_HUB_TOKEN:
            raise ValueError("❌ Hugging Face Hub token is required for this model.")

        repo_id = f"swiss-ai/{model_name}"

        tokenizer = AutoTokenizer.from_pretrained(
            repo_id,
            trust_remote_code=True,
            token=HUGGINGFACE_HUB_TOKEN,
        )

        if quant == "4bit":
            bnb = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                device_map="auto",
                trust_remote_code=True,
                quantization_config=bnb,
                token=HUGGINGFACE_HUB_TOKEN,
            )

        elif quant == "8bit":
            model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                device_map="auto",
                trust_remote_code=True,
                load_in_8bit=True,
                token=HUGGINGFACE_HUB_TOKEN,
            )

        else:
            _, dtype = get_device_and_dtype()
            model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                device_map="auto",
                dtype=dtype,
                trust_remote_code=True,
                token=HUGGINGFACE_HUB_TOKEN,
            )

        text_gen = pipeline(
            task="text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=220,
            temperature=0.2,
            top_k=50,
            top_p=0.8,
            repetition_penalty=1.15,
            do_sample=True,
            return_full_text=False,
        )

        return HuggingFacePipeline(pipeline=text_gen)
    
    def get_llm(
        self, 
        llm_model: str, 
        quant: str | None = None
    ):
        name = (llm_model or "").strip()

        if not name:
            raise ValueError("❌ LLM model name is required.")

        if name.lower() in {
            "apertus-8b-instruct-2509",
            "apertus-70b-instruct-2509",
        }:
            return self._get_hf_llm(name, quant)

        return self._get_ollama_llm(name)
    
    def _build_question_prompt(self) -> PromptTemplate:
        
        template = self.prompt_manager.load_prompt_template(
            CHAT_QUESTION_PROMPT_NAME,
            lang=self.response_language,
        )

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"],
            partial_variables={
                "response_language": lang_display(self.response_language)
            },
        )
    
    @staticmethod
    def _extract_text(response) -> str:
        if response is None:
            print("⚠️ LLM response is None.")
            return ""

        if isinstance(response, str):
            print(f"ℹ️ LLM response is a string: {response}")
            return response.strip()

        content = getattr(response, "content", None)

        if isinstance(content, str):
            print(f"ℹ️ LLM response has 'content' attribute: {content}")
            return content.strip()

        if isinstance(response, dict):
            for key in ("output_text", "text", "output", "result", "answer"):
                value = response.get(key)
                if isinstance(value, str) and value.strip():
                    print(f"ℹ️ LLM response dict has '{key}' key: {value}")
                    return value.strip()
        
        response = str(response).strip()
        print(f"⚠️ Unable to extract text from LLM response, returning raw string: {response}")
        return response 

    async def _invoke_llm(
        self,
        llm, 
        prompt_text: str
    ) -> str:
        try:
            response = await llm.ainvoke(prompt_text)
        except Exception:
            response = await asyncio.to_thread(llm.invoke, prompt_text)
        
        print(f"ℹ️ Raw LLM response: {response}")

        return self._extract_text(response)
    
    async def run_qa(
        self, 
        user_question: str, 
        context_docs: List[str], 
        llm_model: str,
        quant: str | None = None,
    ) -> str:
        """
        Execute QA with given context and return LLM response.
        :param user_question: Input question from user
        :param context_docs: List of strings/chunks retrieved via embeddings
        :param llm_model: Selected LLM model name
        :return: Answer as string
        """
        try:
            print(f"ℹ️ Running QA for question: {user_question} with model: {llm_model} and context: {context_docs}")
            
            llm = self.get_llm(llm_model=llm_model, quant=quant)
            
            prompt = self._build_question_prompt()

            context = "\n\n---\n\n".join(
                chunk.strip()
                for chunk in context_docs
                if isinstance(chunk, str) and chunk.strip()
            )

            prompt_text = prompt.format(
                context=context,
                question=user_question.strip(),
            )

            answer = await self._invoke_llm(llm, prompt_text)

            if not answer:
                print("⚠️ LLM returned an empty response.")
                return "I'm sorry, I couldn't generate a response based on the provided information." if self.response_language == "en" else "Es tut mir leid, ich konnte anhand der bereitgestellten Informationen keine Antwort erstellen."
            
            print(f"✅ Extracted answer text: {answer}")
            return answer
        except Exception as e:
            print(f"❌ Error running QA chain: {str(e)}")
            raise RuntimeError(f"❌ LLM failed to generate response: {str(e)}")
