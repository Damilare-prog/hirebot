import httpx
import numpy as np
import json
from typing import List
from app.core.config import get_settings

settings = get_settings()

async def get_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI's text-embedding-3-small."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.EMBEDDING_MODEL,
                "input": text[:8000],
                "encoding_format": "float"
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

def compute_match_score(profile_embedding: List[float], job_embedding: List[float]) -> float:
    """Convert cosine similarity to 0-100 match score."""
    similarity = cosine_similarity(profile_embedding, job_embedding)
    score = min(100, max(0, int(similarity * 100)))
    return score

def build_profile_text(profile: dict) -> str:
    """Build a rich text representation of a profile for embedding."""
    parts = [
        f"Skills: {', '.join(profile.get('skills', []))}",
        f"Experience: {profile.get('years_experience', 0)} years",
        f"Roles: {', '.join(profile.get('job_titles', []))}",
    ]
    return " ".join(parts)

def build_job_text(job: dict) -> str:
    """Build a rich text representation of a job for embedding."""
    parts = [
        job.get('title', ''),
        job.get('company', ''),
        job.get('description', '')[:2000],
        f"Requirements: {', '.join(job.get('requirements', []))}",
        f"Tags: {', '.join(job.get('tags', []))}",
    ]
    return " ".join(parts)
