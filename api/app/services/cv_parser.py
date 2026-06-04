import httpx
import json
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

CV_PARSE_PROMPT = """You are an expert CV/resume parser. Extract structured information from the document.

Return ONLY a JSON object with this exact structure:
{
  "fullName": "string",
  "email": "string",
  "linkedInUrl": "string or null",
  "phone": "string or null",
  "yearsExperience": number (total years, estimate if needed),
  "skills": ["string"],
  "jobTitles": ["string"],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string or null",
      "year": "string or null"
    }
  ],
  "writingStyle": "string (2-3 sentences of the user's own writing style, extracted from their CV summary or about section)"
}

Rules:
- Extract ALL technical skills, tools, frameworks, languages
- Normalize skill names (e.g., "React.js" -> "React", "TypeScript" -> "TypeScript")
- For yearsExperience: sum all professional roles, round to nearest year
- writingStyle should capture the user's voice for later cover letter generation
"""

async def parse_cv_with_claude(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Send CV to Claude for parsing. In production, use Anthropic's document upload API."""

    # For text-based CVs (PDF text extraction would happen before this)
    # In production: use PyPDF2/pdfplumber to extract text, then send to Claude
    # For now, we simulate with the text content

    text_content = file_bytes.decode('utf-8', errors='ignore')

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": 2000,
                "system": CV_PARSE_PROMPT,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Parse this CV and return structured JSON.\n\nCV CONTENT:\n{text_content[:15000]}"
                    }
                ]
            }
        )
        response.raise_for_status()
        data = response.json()

        # Extract JSON from Claude's response
        content = data["content"][0]["text"]
        # Find JSON block
        start = content.find("{")
        end = content.rfind("}") + 1
        parsed = json.loads(content[start:end])

        return parsed

async def generate_cover_letter(
    user_profile: dict,
    job: dict,
    writing_style: str
) -> str:
    """Generate a tailored cover letter using Claude."""

    prompt = f"""You are an expert career writer. Write a concise, compelling cover letter (150-200 words) for this job application.

CANDIDATE PROFILE:
- Name: {user_profile['full_name']}
- Experience: {user_profile['years_experience']} years
- Skills: {', '.join(user_profile['skills'][:8])}
- Previous roles: {', '.join(user_profile['job_titles'][:3])}

JOB:
- Title: {job['title']}
- Company: {job['company']}
- Description: {job['description'][:2000]}

CANDIDATE'S WRITING STYLE (match this tone):
{writing_style}

Requirements:
- Open with why this specific company/role excites them
- Connect 2-3 specific skills to job requirements
- Show personality matching the writing style
- End with a confident call to action
- Keep it under 200 words
"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
