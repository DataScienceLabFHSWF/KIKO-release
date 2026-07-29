# 🧠 LLM Models

KIKO supports local and remote language model backends for document-based question answering, grading, and document processing.

## 🗂️ Model categories

| Category                   | Purpose                                                   | Example                                    |
| -------------------------- | --------------------------------------------------------- | ------------------------------------------ |
| Embedding model            | Converts text chunks and queries into vectors             | `nomic-embed-text:v1.5`                    |
| Chat / generation model    | Answers user questions using retrieved context            | `llama3.3:70b`, `Apertus-8B-Instruct-2509` |
| Grading / evaluation model | Scores or evaluates learner answers                       | `deepseek-r1:70b`, `nemotron-3-super:120b` |
| Vision-language model      | Processes scanned PDFs, figures, or image-heavy documents | `qwen2.5vl:7b`                             |

## 🖥️ Local Ollama models

KIKO can use Ollama-hosted models through the backend service.

Common examples:

```text
nomic-embed-text:v1.5
qwen2.5vl:7b
llama3.3:70b
nemotron:70b
deepseek-r1:70b
nemotron-3-super:120b
```

## 🤗 Hugging Face models

Some Hugging Face models require an access token or approval from the model owner.

Set the token in .env:

```bash
HUGGINGFACE_HUB_TOKEN=[YOUR_HUGGINGFACE_HUB_TOKEN]
```
