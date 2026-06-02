# MindVault AI

MindVault is a Django-based AI research assistant that combines browser-scraped summaries, saved bookmark collections, and AI chat support with local Ollama integration and optional OpenAI fallback.

## Key Features

- AI-powered webpage summarization
- Saved bookmarks and personal article library
- Local AI chat via Ollama
- Automatic OpenAI fallback when configured
- Admin dashboards for users and bookmarks
- Custom bookmark edit and user management pages

## Tech Stack

- Python 3 / Django 6.0
- Bootstrap 5 / custom CSS
- Ollama local AI model integration
- OpenAI fallback support
- Transformers / Torch for summarization
- BeautifulSoup & Newspaper3k for article parsing

## Requirements

- Python 3.11+ (recommended)
- `venv` or virtual environment
- `ollama` installed for local AI chat

## Installation

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Create a Django superuser:

```powershell
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to view the app.

## Optional Environment Variables

Create a `.env` file in the project root to configure optional services:

```env
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
SERPAPI_API_KEY=...
```

If `OPENAI_API_KEY` is not set, MindVault will still operate with local Ollama and fallback responses.

## Ollama Setup

MindVault is designed to use Ollama for local AI chat first. To install and use Ollama:

1. Download and install Ollama from https://ollama.ai/download
2. Pull a model, for example:

```powershell
ollama pull mistral
```

If your machine has limited RAM, use a smaller model instead:

```powershell
ollama pull orca-mini
```

3. Confirm Ollama is running:

```powershell
curl http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"Hello"}'
```

If Ollama is unavailable, the system will automatically attempt OpenAI.

## Running the App

- Open the web app at `http://127.0.0.1:8000/`
- Signup or login to access the dashboard
- Use the bookmark form to save URLs and generate summaries
- Open the AI chat panel to ask questions
- Use the admin pages to manage users and bookmarks

## Project Structure

- `bookmarks/` — main Django app
- `config/` — Django project settings and URLs
- `static/` — CSS, JS, and frontend assets
- `templates/` — Django templates for pages and admin views
- `OLLAMA_SETUP.md` — Ollama installation and model guidance
- `FINETUNING.md` — custom model fine-tuning instructions

## Troubleshooting

- If you see `CSRF verification failed`, ensure cookies are enabled and refresh the page before submitting the form.
- If chat is not responding, verify Ollama is running at `http://localhost:11434` and that your selected model fits available RAM.
- If Ollama is not available, local chat will fall back to built-in responses, but those are less detailed.
- For slow or failed AI responses, use a smaller Ollama model like `orca-mini` or set `OPENAI_API_KEY` in `.env` to enable OpenAI fallback.

## Notes

- The app uses local summarization and AI responses.
- It is intended for development and evaluation. When deploying to production, secure your `.env`, enable HTTPS, and set `DEBUG = False`.

---

If you want, I can also add a short `CONTRIBUTING.md` or GitHub issue template for this repo.