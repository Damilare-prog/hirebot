import json
import io
from typing import Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from google import genai
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
        return file_bytes.decode('utf-8', errors='ignore')

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or text file."""
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    else:
        return file_bytes.decode('utf-8', errors='ignore')

async def parse_cv_with_gemini(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Send CV to Gemini for parsing using new google.genai package."""
    
    if genai is None:
        raise ImportError("google.genai is not installed. Run: pip install google-genai")
    
    # Extract text from file
    text_content = extract_text_from_file(file_bytes, filename)
    
    if not text_content or len(text_content.strip()) < 50:
        raise ValueError("Could not extract text from CV. Please upload a text-based PDF or .txt file.")
    
    # Configure Gemini
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    prompt = f"""{CV_PARSE_PROMPT}

Parse this CV and return ONLY the JSON object:

CV CONTENT:
{text_content[:15000]}
"""
    
    response = await client.aio.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    
    # Extract JSON from response
    content = response.text
    
    # Find JSON block
    start = content.find("{")
    end = content.rfind("}") + 1
    
    if start == -1 or end == 0:
        raise ValueError("Could not parse JSON from Gemini response")
    
    parsed = json.loads(content[start:end])
    
    return parsed

async def generate_cover_letter(
    user_profile: dict,
    job: dict,
    writing_style: str
) -> str:
    """Generate a tailored cover letter using Gemini."""
    
    if genai is None:
        raise ImportError("google.genai is not installed")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
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
    
    response = await client.aio.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    
    return response.text.strip()
