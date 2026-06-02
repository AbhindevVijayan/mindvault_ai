# Local AI Setup with Ollama

## Step 1: Install Ollama

1. Download from: https://ollama.ai/download (Windows installer available)
2. Install and restart your computer
3. Ollama will start running in the background on `http://localhost:11434`

## Step 2: Pull a Model

Open PowerShell and run:
```powershell
ollama pull mistral
```

Or for faster responses with less memory, use:
```powershell
ollama pull neural-chat
```

Or for lighter weight:
```powershell
ollama pull orca-mini
```

## Step 3: Verify Installation

```powershell
# Test the model is running
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"Hello"}'
```

You should see a response with generated text.

## Step 4: Environment Setup

The Django app will automatically detect Ollama running on `localhost:11434` and use it for chat.

## Model Options

- **mistral** - Fast, 7B params, good quality (~5GB)
- **neural-chat** - Conversational, ~4GB, optimized for chat
- **orca-mini** - Lightweight, 3B params, ~2GB, good for low-end machines
- **llama2** - Powerful, 7B params, ~4GB

Smaller models = faster responses but less intelligent. Start with `mistral` or `neural-chat`.

## Fine-tuning (Optional)

After the app is working, you can fine-tune with your own Q&A data:

1. Create training data (Q&A pairs about your app)
2. Use `ollama create` command to build a custom model
3. Deploy the fine-tuned model

See the FINETUNING.md file for details.
