from newspaper import Article

def extract_article(url):

    article = Article(url)

    article.download()

    article.parse()

    return {
        "title": article.title,
        "content": article.text
    }
    
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="distilgpt2"
)

def generate_summary(text):

    prompt = f"Summarize this article briefly:\n{text[:500]}"

    result = generator(
        prompt,
        max_length=150,
        num_return_sequences=1
    )

    return result[0]['generated_text']


from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

def generate_embedding(text):

    embedding = embedding_model.encode(text)

    return embedding.tolist()

import numpy as np

def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    similarity = np.dot(vec1, vec2) / (
        np.linalg.norm(vec1)
        * np.linalg.norm(vec2)
    )

    return similarity