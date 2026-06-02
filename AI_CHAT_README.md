# MindVault - Local AI Chat Integration

This project uses **Ollama** for local, offline AI chat capabilities alongside optional OpenAI API support.

## Quick Start

### 1. Install Ollama (One-time Setup)

1. Download from https://ollama.ai/download
2. Install and restart your computer
3. Ollama will run automatically in the background

### 2. Pull a Model

Open PowerShell and run:

```powershell
ollama pull mistral
```

Other options:
- `ollama pull neural-chat` - Faster, optimized for conversation
- `ollama pull orca-mini` - Lightweight, ~2GB

### 3. Verify Setup

Test that Ollama is running:

```powershell
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"Hello"}'
```

You should see a response with generated text.

### 4. Run Django

```powershell
python manage.py runserver
```

The chat system will automatically:
1. Try local Ollama first (fast, offline, free)
2. Fall back to OpenAI API if OPENAI_API_KEY is set
3. Fall back to rule-based responses

## Chat Flow

```
User Question
    ↓
[1] Try Local Ollama (localhost:11434)
    ├─ Success? → Return Ollama response
    └─ Failed/Offline? → Continue
       ↓
[2] Try OpenAI API (if OPENAI_API_KEY set)
    ├─ Success? → Return OpenAI response
    └─ Failed/No key? → Continue
       ↓
[3] Rule-based Fallback
    └─ Return pattern-matched response
```

## Environment Variables (Optional)

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
SERPAPI_API_KEY=...
```

If no `.env` is present, the app works perfectly with just local Ollama!

## Files

- **OLLAMA_SETUP.md** - Detailed installation and model selection guide
- **FINETUNING.md** - How to create custom fine-tuned models with your data
- **bookmarks/utils.py** - Contains `_call_ollama()` and `chat_response()` functions

## Advanced: Fine-Tuning

To create a model trained on your own Q&A data:

```powershell
# 1. Create training data and Modelfile
# See FINETUNING.md for details

# 2. Build custom model
ollama create mindvault-custom -f Modelfile

# 3. Update bookmarks/utils.py to use 'mindvault-custom'
# Change: 'model': 'mistral' → 'model': 'mindvault-custom'

# 4. Restart Django
python manage.py runserver
```

## Troubleshooting

**Chat not responding?**
- Check if Ollama is running: http://localhost:11434/api/generate
- If offline, responses will still work via fallback

**Slow responses?**
- Using mistral? Try `ollama pull neural-chat` for faster responses
- Local models typically take 2-5 seconds per response

**Hallucinating incorrect information?**
- Create fine-tuned model with accurate training data
- See FINETUNING.md for instructions

**Want to use OpenAI instead?**
- Set `OPENAI_API_KEY` in `.env`
- System will automatically use OpenAI while Ollama is unavailable

## Performance Notes

- **Ollama (local)**: 2-5s per response, no API costs, works offline
- **OpenAI**: <1s per response, requires API key, costs money
- **Fallback**: <100ms, limited patterns, always works

## Next Steps

1. Complete OLLAMA_SETUP.md
2. Test chat in dashboard
3. (Optional) Create fine-tuned model using FINETUNING.md
4. Enjoy your local AI assistant!
