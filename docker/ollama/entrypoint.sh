#!/bin/bash
set -e

# Default port fallback if not set
OLLAMA_PORT="${OLLAMA_PORT:-11434}"

echo "🚀 Starting Ollama server in background..."
ollama serve &

# Wait for Ollama API to become available
until curl -s http://localhost:${OLLAMA_PORT} > /dev/null; do
  echo "⌛ Waiting for Ollama server to start on port ${OLLAMA_PORT}..."
  sleep 2
done

echo "✅ Ollama server is up on port ${OLLAMA_PORT}, pulling models..."
# Pull models

# nomic-embed-text is a large context length text encoder that surpasses OpenAI text-embedding-ada-002 and text-embedding-3-small performance on short and long context tasks.
# https://ollama.com/library/nomic-embed-text
ollama pull ${EMBEDDING_MODEL_NAME}

# VLM models are designed to handle and generate content that involves both text and images.
# Qwen2.5-VL, the new flagship vision-language model of Qwen and also a significant leap from the previous Qwen2-VL.
# https://ollama.com/library/qwen2.5vl:7b
ollama pull ${VLM_MODEL_NAME}

# The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text out).
# The Llama 3.3 instruction tuned text only model is optimized for multilingual dialogue use cases and outperform 
# many of the available open source and closed chat models on common industry benchmarks.
# https://ollama.com/library/llama3.3:70b
ollama pull ${LLAMA_LLM_GENERATION_MODEL_NAME}

# Llama-3.1-Nemotron-70B-Instruct is a large language model customized by NVIDIA to improve the helpfulness of LLM generated responses to user queries.
# https://ollama.com/library/nemotron 
ollama pull ${NEMOTRON_LLM_GENERATION_MODEL_NAME}

# DeepSeek-R1 is a 32B parameter LLM optimized for reasoning tasks,
# excelling in complex problem-solving, logical reasoning, and multi-step inference.
# https://ollama.com/library/deepseek-r1:70b
ollama pull ${DEEPSEEK_LLM_GRADING_INFERENCE_MODEL_NAME}

# Gemma 3 models excel in tasks like question answering, summarization, and reasoning, 
# while their compact design allows deployment on resource-limited devices.
# https://ollama.com/library/gemma3:12b
# ollama pull gemma3:12b

# Nemotron-3-Super is a large language model (LLM) trained y NVIDIA, designed to deliver strong agentic, reasoning, and conversational capabilities.
# Like other models in the family, it responds to user queries and tasks by first generating a reasoning trace and then concluding with a final response.
# The model has 12B active parameters and 120B parameters in total.
# https://ollama.com/library/nemotron-3-super
ollama pull ${NEMOTRON_LLM_GRADING_INFERENCE_MODEL_NAME}


echo "✅ Models pulled successfully. Ollama is ready 🚀"

# Keep the script running to keep the container alive
tail -f /dev/null
