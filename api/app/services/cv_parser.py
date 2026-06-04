import json
import io
from typing import Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

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

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyPDF2."""
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        # Fallback: try to decode as text
        return file_bytes.decode('utf-8', errors='ignore')

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or text file."""
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    else:
        # For .txt, .docx (basic), etc.
        return file_bytes.decode('utf-8', errors='ignore')

async def parse_cv_with_gemini(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Send CV to Gemini for parsing."""
    
    if genai is None:
        raise ImportError("google-generativeai is not installed. Run: pip install google-generativeai")
    
    # Extract text from file
    text_content = extract_text_from_file(file_bytes, filename)
    
    if not text_content or len(text_content.strip()) < 50:
        raise ValueError("Could not extract text from CV. Please upload a text-based PDF or .txt file.")
    
    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    model = genai.GenerativeModel('gemini-1.5-flash')  # Free tier model
    
    prompt = f"""{CV_PARSE_PROMPT}

Parse this CV and return ONLY the JSON object:

CV CONTENT:
{text_content[:15000]}
"""
    
    response = await model.generate_content_async(prompt)
    
    # Extract JSON from response
    content = response.text
    
    # Find JSON block
    start = content.find("{")
    end = content.rfind("}") + 1
    
    if start == -1 or end == 0:
        raise ValueError("Could not parse JSON from Gemini response")
    
    parsed = json.loads(content[start:end])
    
    return parsed

async def parse_cv_with_claude(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Fallback to Claude if Gemini fails."""
    # Keep the old Claude function as fallback
    import httpx
    
    text_content = extract_text_from_file(file_bytes, filename)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.CLAUDE_MODEL or "claude-3-sonnet-20240229",
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

        content = data["content"][0]["text"]
        start = content.find("{")
        end = content.rfind("}") + 1
        parsed = json.loads(content[start:end])

        return parsed

async def generate_cover_letter(
    user_profile: dict,
    job: dict,
    writing_style: str
) -> str:
    """Generate a tailored cover letter using Gemini (free tier)."""
    
    if genai is None:
        raise ImportError("google-generativeai is not installed")
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
    
    response = await model.generate_content_async(prompt)
    return response.text.strip()
