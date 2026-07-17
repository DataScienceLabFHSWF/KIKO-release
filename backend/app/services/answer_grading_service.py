# backend/app/services/answer_grading_service.py
import os, time, re
from typing import Optional, Tuple, Dict, Any
from ollama import Client
from .configuration_service import get_app_config_and_libary_available
from app.core import PromptManager
from app.utils import lang_display

DOCKER_OLLAMA_URL = os.getenv("DOCKER_OLLAMA_URL")
LLM_GRADING_INFERENCE_MODEL_NAME = os.getenv("NEMOTRON_LLM_GRADING_INFERENCE_MODEL_NAME")
GRADING_EVAL_PROMPT_NAME = "grading_eval_prompt"
GRADING_OPTIMIZE_EVAL_PROMPT_NAME = "grading_optimize_eval_prompt"

GRADE_RE = re.compile(
    r"""(?mi)          # multi-line, case-insensitive
    \b(?:note|grade)\b # 'Note' (DE) or 'Grade' (EN)
    [^\d]*             # anything until a digit
    ([1-6])            # capture 1..6
    (?:\s*\([^)]+\))?  # optional '(befriedigend)' etc.
    """,
    re.VERBOSE,
)

def extract_grade(summary: str) -> Optional[int]:
    """Extracts the grade from the summary string."""
    
    print(f"ℹ️ extract_grade from summary: {summary}")

    if not summary:
        return None
    m = GRADE_RE.search(summary)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None

def normalize_grade_items(summary: str) -> Tuple[Optional[int], Optional[str]]:
    """Normalizes the grade and summary from the provided text."""
    
    if not summary:
        return 0, summary
    
    grade = extract_grade(summary)
    
    if grade is None:
        return 0, summary
    
    print(f"✅ Normalized grade: {grade} from summary: {summary}")

    return int(grade), summary.strip()

def current_timestamp() -> str:
    """
    Returns the current timestamp as a formatted string in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: A string representing the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'.

    Example:
        current_timestamp()
        '2025-03-02 12:34:56'
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def get_ollama_client_and_model(model_name) -> Tuple[Client, str]:
    """
    Connects to the Ollama daemon and returns (client, model_tag).
    - Host: DOCKER_OLLAMA_URL
    - Model: model_name
    """
    client = Client(host=DOCKER_OLLAMA_URL)
    
    if model_name is None:
        model_name = LLM_GRADING_INFERENCE_MODEL_NAME
    
    print(f"ℹ️ Selected Inference model: {model_name}")
    return client, model_name

def _ollama_chat(
    client: Client,
    model_tag: str,
    prompt: str,
    max_tokens: int,
    temperature: float = 0.2
) -> str:
    """Sends a chat prompt to the Ollama model and returns the response text."""
    print(f"ℹ️ Sending prompt to Ollama model: {model_tag} with temperature: {temperature} and max_tokens: {max_tokens}")
    try:
        # Note: Ollama's num_predict is the max tokens in the response
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
            "top_k": 50,
            "top_p": 0.95,
        }
        
        # Send the chat request
        resp = client.chat(
            model=model_tag,
            messages=[{"role": "user", "content": prompt}],
            options=options,
        )

        # Extract the response text
        text = resp.get("message", {}).get("content", "").strip()

        print(f"✅ Ollama response received ({len(text)} chars).")

        return text
    except Exception as e:
        print(f"❌ Ollama chat error: {e}")
        return f"Error: {e}"

def format_prompt(tmpl: str, **kwargs) -> str:
    try:
        return tmpl.format(**kwargs)
    except Exception:
        # If template uses {json}-style braces, safe fallback without crashing
        return tmpl

def strip_think_block(text: str) -> str:
    """
    Removes a leading <think>...</think> block if present.
    Keeps the final answer clean for downstream grade parsing.
    """
    if not text:
        return text
    start = text.find("<think>")
    end = text.find("</think>")
    if start != -1 and end != -1 and end > start:
        return text[end + len("</think>"):].strip()
    return text

def ensure_think_then_answer(
    client: Client,
    model_tag: str,
    prompt: str,
    no_think_max_tokens: int,
    max_retries: int = 1
) -> str:
    """Ensures the response contains a <think>...</think> block, retrying if necessary."""
    
    resp = _ollama_chat(client, model_tag, prompt, no_think_max_tokens)
    retries = 0
    while "</think>" not in resp and retries < max_retries:
        # Log for visibility, similar to your original code
        try:
            get_cwd = os.getcwd()
            logs_path = os.path.join(get_cwd, "backend/data/logs/")
            os.makedirs(logs_path, exist_ok=True)
            log_file = os.path.join(logs_path, "incomplete_think_log.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[{current_timestamp()}] Retry {retries+1} — Missing '</think>' tag.\n")
                f.write(f"Prompt:\n{prompt}\n\n {'='*25} \nFailed Response:\n{resp}\n{'='*80}\n")
        except Exception:
            pass
        
        resp = _ollama_chat(client, model_tag, prompt, no_think_max_tokens)
        retries += 1
    print(f"✅ ensure_think_then_answer: retries={retries} and final response={resp}")
    return resp

def generate_response(
    prompt: str,
    client: Client,
    model_tag: str,
    no_max_tokens: int,
    remove_think_block:bool = True
) -> Tuple[str, int]:
    """Generates a response from the model based on the given prompt."""
    print(f"ℹ️ Generating response with Ollama model: {model_tag}")
    
    # Optionally ensure think block; set max_retries=0 if you don't care
    full_text = ensure_think_then_answer(client, model_tag, prompt, no_max_tokens, max_retries=1)
    
    if remove_think_block:
        full_text = strip_think_block(full_text)
    
    # Estimate tokens as number of words (approximation)
    generated_tokens_est = max(0, len(full_text.split()))
    
    print(f"✅ generate_response: tokens≈{generated_tokens_est}")
    
    return full_text, generated_tokens_est

def evaluate_user_answer(
    question: str,
    user_answer: str,
    reference_answer: Optional[str],
    client: Client,
    model_tag: str,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> str:
    """Evaluates a user's answer to a question using a language model."""
    # Load evaluation prompt template
    template = prompt_manager.load_prompt_template(GRADING_EVAL_PROMPT_NAME, lang=response_language)
    
    # Format the prompt with the question, user answer, and reference answer
    eval_prompt = format_prompt(
        template, 
        question=question, 
        user_answer=user_answer, 
        reference_answer=(reference_answer or ""),
        language=lang_display(response_language)
    )

    print(f"ℹ️ eval_prompt:\n{eval_prompt} and loaded template: {template}")

    # Generate the evaluation response
    feedback, _ = generate_response(eval_prompt, client, model_tag, no_max_tokens)

    print(f"✅ evaluate_user_answer() — feedback:\n{feedback}")

    return feedback

def optimizer_refine_grading(
    question: str, 
    user_answer: str,
    grading: str, 
    client: Client, 
    model_tag: str, 
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> str:
    """Refines the grading feedback using an optimizer prompt."""
    
    # Load optimization prompt template
    template = prompt_manager.load_prompt_template(GRADING_OPTIMIZE_EVAL_PROMPT_NAME, lang=response_language)

    # Format the prompt with the question, user answer, and current grading
    opt_prompt = format_prompt(
        template, 
        question=question, 
        user_answer=user_answer, 
        grading=grading,
        language=lang_display(response_language)
    )

    print(f"ℹ️ opt_prompt:\n{opt_prompt} and loaded template: {template}")
    
    # Generate the improved grading response
    improved_response, _ = generate_response(opt_prompt, client, model_tag, no_max_tokens)

    print(f"✅ optimizer_refine_grading() — improved:\n{improved_response}")

    return improved_response

# Evaluator-Optimizer Grading Loop
def evaluator_optimizer_grading_loop(
    question: str, 
    user_answer: str, 
    reference_answer: Optional[str], 
    client: Client, 
    model_tag: str,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str,
    max_iters: int = 1    
):
    """Grades a user's answer using an evaluator-optimizer loop."""
    print(f"ℹ️ Starting evaluator_optimizer_grading_loop with max_iters={max_iters}")

    grading = evaluate_user_answer(
        question=question,
        user_answer=user_answer,
        reference_answer=reference_answer,
        client=client,
        model_tag=model_tag,
        prompt_manager=prompt_manager,
        no_max_tokens=no_max_tokens,
        response_language=response_language
    )

    print(f"ℹ️ Initial grading:\n{grading}")

    grading_summary = grading
    for i in range(max_iters):
        print(f"ℹ️ Optimization iteration: {i+1}/{max_iters}")
        
        grading_summary = optimizer_refine_grading(
            question=question,
            user_answer=user_answer,
            grading=grading_summary,
            client=client,
            model_tag=model_tag,
            prompt_manager=prompt_manager,
            no_max_tokens=no_max_tokens,
            response_language=response_language
        )
    
    grade_class_info, grade_summary = normalize_grade_items(grading_summary)
    print(f"✅ Final grading summary: {grading_summary}\nParsed grade: {grade_class_info}")
    return grade_class_info, grade_summary

async def grade_user_answer(
    question: str,
    user_answer: str,
    inference_model_name:str,
    reference_answer: str,
    no_max_tokens: int,
    response_language: str
) -> Dict[str, Any]:
    """Grades a user's answer to a question using a reasoning-optimized language model."""
    # Heavy reasoning, good for evaluation tasks.
    # DeepSeek-R1-Distill-Qwen-32B is reasoning-optimized
    quant_config = None
    
    # Load model and tokenizer
    model_loading_start_time = time.time()
    
    client, model_tag = get_ollama_client_and_model(inference_model_name)
    
    model_loading_time = time.time() - model_loading_start_time
    
    print(f"ℹ️ Model loaded for grade_user_answer: {model_tag}, loading time: {model_loading_time} and Max Tokens: {no_max_tokens}")

    configs = await get_app_config_and_libary_available()
    
    prompt_mgr = PromptManager(configs)
    
    grade_class, grade_summary = evaluator_optimizer_grading_loop(
        question=question, 
        user_answer=user_answer,
        reference_answer=reference_answer,
        client=client,
        model_tag=model_tag,
        prompt_manager=prompt_mgr,
        no_max_tokens=no_max_tokens,
        response_language=response_language
    )
    
    response: Dict[str, Any] = {
        "grade": grade_class,
        "summary": grade_summary
    }
    
    print(f"✅ Final grade_user_answer grading generated: {response}")
    return response
