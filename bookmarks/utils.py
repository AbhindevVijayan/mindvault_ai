def extract_article(url):
    try:
        from newspaper import Article
        article = Article(url)
        article.download()
        article.parse()

        if article.title and article.text:
            return {
                "title": article.title,
                "content": article.text
            }
    except ImportError as exc:
        if 'lxml.html.clean' in str(exc) or 'lxml_html_clean' in str(exc):
            return extract_article_fallback(url)
        raise
    except Exception:
        return extract_article_fallback(url)

    return extract_article_fallback(url)


def extract_article_fallback(url):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
    }, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'svg', 'form', 'img', 'figure', 'aside', 'nav']):
        tag.decompose()

    paragraphs = [p.get_text(' ', strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
    content = '\n\n'.join(paragraphs).strip()

    if not content:
        content = soup.get_text(' ', strip=True)

    return {
        'title': title,
        'content': content[:20000]
    }
    

def _normalize_summary(text):
    import re

    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = []
    seen = set()

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        normalized = sentence.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned_sentences.append(sentence)

    summary = ' '.join(cleaned_sentences).strip()
    if summary.endswith('..'):
        summary = summary.rstrip('.') + '.'

    return summary


def _extractive_summary(text, max_sentences=3, max_words=80):
    import re

    text = (text or '').strip()
    if not text:
        return ''

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if sentences:
        return ' '.join(sentences[:max_sentences])

    words = text.split()
    if len(words) <= max_words:
        return text

    return ' '.join(words[:max_words]) + '...'


def _has_repeated_sentences(text):
    import re

    text = (text or '').strip()
    if not text:
        return False

    sentences = [s.strip().lower() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    return len(sentences) != len(set(sentences))


def generate_summary(text):
    text = (text or '').strip()
    if not text:
        return ''

    try:
        from transformers import pipeline

        summarizer = pipeline(
            'summarization',
            model='sshleifer/distilbart-cnn-12-6'
        )
        result = summarizer(
            text[:1600],
            max_length=150,
            min_length=50,
            do_sample=False
        )
        summary = result[0].get('summary_text', '')
        if _has_repeated_sentences(summary):
            return _normalize_summary(_extractive_summary(text))
        return _normalize_summary(summary)
    except Exception:
        try:
            from transformers import GenerationConfig, pipeline
            generator = pipeline('text-generation', model='distilgpt2')
            prompt = f"Summarize this article briefly:\n{text[:500]}"
            gen_config = GenerationConfig(
                max_new_tokens=120,
                num_return_sequences=1,
                pad_token_id=50256
            )
            result = generator(
                prompt,
                generation_config=gen_config,
                return_full_text=False,
                clean_up_tokenization_spaces=False
            )
            summary = result[0]['generated_text'].strip()
            if _has_repeated_sentences(summary):
                return _normalize_summary(_extractive_summary(text))
            return _normalize_summary(summary)
        except Exception:
            return _normalize_summary(_extractive_summary(text))


def _call_ollama(question, context_snippets=''):
    """Call local Ollama model for chat inference."""
    try:
        import requests
        import json
        import os

        ollama_url = 'http://127.0.0.1:11434/api/generate'
        system_prompt = (
            'You are a helpful AI assistant for MindVault, an article summarization and smart search platform. '
            'Answer user questions clearly, concisely, and helpfully. '
            'Focus on helping with article summaries, bookmarks, and smart search features.'
        )

        if context_snippets:
            system_prompt += '\n\nReference information:\n' + context_snippets

        full_prompt = f"{system_prompt}\n\nUser: {question}\nAssistant:"

        model_name = os.getenv('OLLAMA_MODEL', 'orca-mini')

        payload = {
            'model': model_name,
            'prompt': full_prompt,
            'stream': False,
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'num_ctx': 2048,
            'num_predict': 256
        }

        response = requests.post(ollama_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            reply = result.get('response', '').strip()
            if reply:
                return reply
        else:
            error_text = response.text.strip().lower()
            if 'model requires more system memory' in error_text or 'memory' in error_text:
                return (
                    'Ollama failed because the selected model needs more memory than is available. '
                    'Try a smaller model, for example: OLLAMA_MODEL=orca-mini and run `ollama pull orca-mini`.'
                )
    except Exception:
        pass

    try:
        import subprocess
        import json
        model_name = os.getenv('OLLAMA_MODEL', 'orca-mini')
        proc = subprocess.run(
            ['ollama', 'run', model_name, full_prompt, '--format', 'json'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=20
        )
        output = (proc.stdout or '') + (proc.stderr or '')
        if proc.returncode == 0 and proc.stdout:
            try:
                parsed = json.loads(proc.stdout)
                for msg in reversed(parsed.get('messages', [])):
                    if msg.get('role') == 'assistant' and msg.get('content'):
                        return msg['content'].strip()
                response_text = parsed.get('response')
                if isinstance(response_text, str) and response_text.strip():
                    return response_text.strip()
            except Exception:
                return proc.stdout.strip()
        if 'model requires more system memory' in output.lower() or 'memory' in output.lower():
            return (
                'Ollama failed because the selected model needs more memory than is available. '
                'Try a smaller model, for example: OLLAMA_MODEL=orca-mini and run `ollama pull orca-mini`.'
            )
    except Exception:
        pass

    return None


def _basic_chat_fallback(question):
    question_norm = (question or '').strip().lower()
    if not question_norm:
        return 'Ask me anything and I will answer.'

    greetings = ['hello', 'hi', 'hey', 'hiya', 'good morning', 'good afternoon', 'good evening']
    if any(g in question_norm for g in greetings):
        return 'Hello! I am your MindVault assistant. Ask me about article summaries, saved bookmarks, or smart search.'
    if 'how are you' in question_norm or 'how r you' in question_norm or 'how you' in question_norm:
        return 'I am ready to help. Ask me anything about summarizing articles or organizing your saved content.'
    if 'summary' in question_norm or 'summarize' in question_norm:
        return 'I can summarize articles for you. Paste a URL into the summary box and I will generate one instantly.'
    if 'bookmark' in question_norm or 'save' in question_norm:
        return 'You can save articles to your library using the summary form, then ask me about your saved articles.'
    if 'openai' in question_norm or 'api key' in question_norm or 'key' in question_norm:
        return 'You can use either a local Ollama model or OpenAI API. Local models work offline and free - set up Ollama for best results!'
    if 'ollama' in question_norm or 'local' in question_norm or 'offline' in question_norm:
        return 'Ollama provides local AI models that run offline. Install from https://ollama.ai and run: ollama pull mistral'
    return 'I could not generate a detailed answer here. For best results, set up local Ollama models or enable OPENAI_API_KEY.'


def chat_response(question):
    import os
    question = (question or '').strip()
    if not question:
        return 'Ask me anything and I will answer.'

    # Try using SerpAPI to gather up-to-date web context (optional)
    context_snippets = ''
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    if serpapi_key:
        try:
            from serpapi import GoogleSearch
            params = {
                'q': question,
                'api_key': serpapi_key,
                'engine': 'google',
                'num': 5
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            snippets = []
            for r in results.get('organic_results', [])[:5]:
                title = r.get('title', '')
                snippet = r.get('snippet') or r.get('snippet_text') or ''
                link = r.get('link', '')
                if snippet:
                    snippets.append(f"{title}: {snippet} ({link})")
            context_snippets = '\n\n'.join(snippets)[:3000]
        except Exception:
            context_snippets = ''

    # Priority 1: Try local Ollama first (offline, free, fast)
    ollama_reply = _call_ollama(question, context_snippets)
    if ollama_reply:
        return ollama_reply

    # Priority 2: Fall back to OpenAI if available
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            import openai
            openai.api_key = openai_key
            messages = []
            system_msg = 'You are an expert assistant. Answer concisely and cite facts when possible.'
            if context_snippets:
                system_msg += '\nThe following search snippets may be helpful:\n' + context_snippets
            messages.append({'role': 'system', 'content': system_msg})
            messages.append({'role': 'user', 'content': question})

            resp = openai.ChatCompletion.create(
                model=os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini'),
                messages=messages,
                temperature=0.2,
                max_tokens=600
            )
            text = resp['choices'][0]['message']['content'].strip()
            return text
        except Exception:
            pass

    # Priority 3: Fall back to rule-based responses
    return _basic_chat_fallback(question)


def generate_embedding(text):
    try:
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = embedding_model.encode(text)
        return embedding.tolist()
    except Exception:
        return []

import numpy as np

def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    similarity = np.dot(vec1, vec2) / (
        np.linalg.norm(vec1)
        * np.linalg.norm(vec2)
    )

    return similarity
