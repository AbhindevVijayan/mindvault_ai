# Fine-Tuning a Local AI Model with Your Data

After Ollama is working with the base model (mistral), you can fine-tune it with your own Q&A data for better performance on your specific domain.

## Quick Start

### Step 1: Create Training Data

Create a file `training_data.txt` with Q&A pairs (one per line):

```txt
Q: How do I summarize an article?
A: Click "Add Bookmark", paste the article URL, and click "Summarize". The AI will extract and summarize the content.

Q: How do I search my saved bookmarks?
A: Use the search box on the dashboard to find bookmarks by keyword, content, or tags.

Q: What is semantic search?
A: Semantic search uses AI to understand the meaning of your query and find related articles, even with different wording.

Q: How do I create a saved collection?
A: Save articles through the summary form, then organize them using tags and collections on your dashboard.

Q: Can I export my bookmarks?
A: You can export your saved articles as JSON or CSV from the settings page.
```

Expand this with 50+ Q&A pairs from your documentation, FAQs, and typical user questions.

### Step 2: Convert to Ollama Format

Create `training.jsonl` (JSON Lines format):

```jsonl
{"prompt": "Q: How do I summarize an article?\nA:", "completion": " Click \"Add Bookmark\", paste the article URL, and click \"Summarize\". The AI will extract and summarize the content."}
{"prompt": "Q: How do I search my saved bookmarks?\nA:", "completion": " Use the search box on the dashboard to find bookmarks by keyword, content, or tags."}
```

Or use this Python script to auto-convert:

```python
import json

with open('training_data.txt', 'r') as f:
    pairs = f.read().strip().split('\n\n')

with open('training.jsonl', 'w') as out:
    for pair in pairs:
        lines = pair.strip().split('\n')
        if len(lines) >= 2:
            q = lines[0].replace('Q: ', '').strip()
            a = '\n'.join(lines[1:]).replace('A: ', '').strip()
            json.dump({'prompt': f'Q: {q}\nA:', 'completion': f' {a}'}, out)
            out.write('\n')

print("training.jsonl created successfully")
```

### Step 3: Create a Custom Model

1. Create a `Modelfile` in your project root:

```
FROM mistral
PARAMETER temperature 0.3
PARAMETER top_k 20
PARAMETER num_ctx 4096
SYSTEM """You are a helpful assistant for MindVault, an article summarization platform. Answer user questions about summarizing, searching, and organizing articles. Be concise and helpful."""
```

2. Build the model:

```powershell
cd c:\Users\HP\mindvault_ai
ollama create mindvault-custom -f Modelfile
```

3. Test it:

```powershell
ollama run mindvault-custom "How do I summarize an article?"
```

### Step 4: Use the Custom Model in Django

Update `bookmarks/utils.py` in the `_call_ollama()` function, change:

```python
'model': 'mistral',  # Change to 'mindvault-custom'
```

To:

```python
'model': 'mindvault-custom',
```

Then restart your Django app:

```powershell
python manage.py runserver
```

## Advanced Fine-Tuning

For production-grade fine-tuning, use **LoRA (Low-Rank Adaptation)**:

1. Install fine-tuning tools:
   ```powershell
   pip install peft transformers torch
   ```

2. Follow Hugging Face LoRA guide: https://huggingface.co/docs/peft/conceptual_guides/lora

3. Export fine-tuned weights and merge with base model

4. Use Ollama's import feature to load the merged model

## Monitoring Performance

After deployment, track:

- **Response quality**: Are answers relevant and accurate?
- **Response time**: Should be 1-5 seconds on typical hardware
- **Memory usage**: Monitor with `ollama ps`
- **Hallucination rate**: Do responses make up false facts?

## Troubleshooting

**Model runs slowly**: Use a smaller base model (orca-mini instead of mistral)

**Poor answers on your domain**: Expand training data to 100+ examples

**Out of memory**: Reduce `num_ctx` in Modelfile (2048 instead of 4096)

**Model forgets fine-tuned behavior**: Run `ollama pull mindvault-custom` to reload

## Next Steps

1. Collect real Q&A pairs from your application
2. Create and test a custom model
3. Measure quality improvements
4. Deploy to production when confident
