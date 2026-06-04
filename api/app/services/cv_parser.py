# cv_parser.py - Simple version, no AI needed
import json
import io
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyPDF2."""
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is not installed")
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or text file."""
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    else:
        return file_bytes.decode('utf-8', errors='ignore')

def parse_cv_simple(file_bytes: bytes, filename: str) -> dict:
    """Parse CV using simple regex patterns - no AI needed."""
    
    text = extract_text_from_file(file_bytes, filename)
    
    # Extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else "unknown@email.com"
    
    # Extract phone
    phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    phone = phone_match.group(0) if phone_match else None
    
    # Extract LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9\-]+', text)
    linkedin = linkedin_match.group(0) if linkedin_match else None
    
    # Extract name (first line or capitalized words)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    full_name = lines[0] if lines else "Unknown Name"
    
    # Extract skills (common tech keywords)
    skill_keywords = [
        'python', 'javascript', 'typescript', 'react', 'node.js', 'nodejs', 'sql',
        'postgresql', 'mongodb', 'aws', 'docker', 'kubernetes', 'git', 'html',
        'css', 'tailwind', 'next.js', 'fastapi', 'django', 'flask', 'redis',
        'graphql', 'rest', 'api', 'linux', 'bash', 'nginx', 'jenkins', 'ci/cd',
        'terraform', 'ansible', 'prometheus', 'grafana', 'elasticsearch', 'kafka',
        'rabbitmq', 'celery', 'pandas', 'numpy', 'scikit-learn', 'tensorflow',
        'pytorch', 'opencv', 'nlp', 'machine learning', 'deep learning', 'ai',
        'data science', 'data analysis', 'tableau', 'powerbi', 'excel', 'figma',
        'sketch', 'adobe', 'photoshop', 'illustrator', 'ui/ux', 'product design',
        'agile', 'scrum', 'jira', 'confluence', 'notion', 'slack', 'teams'
    ]
    
    text_lower = text.lower()
    skills = []
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title())
    
    # Extract years of experience
    years_match = re.search(r'(\d+)\+?\s*years?', text_lower)
    years = int(years_match.group(1)) if years_match else 0
    
    # Extract job titles
    job_titles = []
    title_patterns = [
        r'(?:Senior|Junior|Lead|Principal|Staff)?\s*(Software|Frontend|Backend|Full-Stack|DevOps|Data|ML|AI|Product|UI/UX|Web|Mobile)?\s*(Engineer|Developer|Designer|Manager|Architect|Scientist|Analyst)',
        r'(?:Senior|Junior|Lead|Principal)?\s*(Developer|Engineer|Designer|Manager)',
    ]
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                title = ' '.join(filter(None, match))
            else:
                title = match
            if title and title not in job_titles:
                job_titles.append(title.title())
    
    return {
        "fullName": full_name,
        "email": email,
        "linkedInUrl": linkedin,
        "phone": phone,
        "yearsExperience": years,
        "skills": skills[:20],  # Limit to 20 skills
        "jobTitles": job_titles[:5],
        "education": [],
        "writingStyle": "Professional and detail-oriented."
    }

async def parse_cv_with_gemini(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Wrapper for simple parsing."""
    return parse_cv_simple(file_bytes, filename)

async def generate_cover_letter(user_profile: dict, job: dict, writing_style: str) -> str:
    """Generate a simple cover letter without AI."""
    return f"""Dear Hiring Manager,

I am excited to apply for the {job['title']} position at {job['company']}. With {user_profile['years_experience']} years of experience and expertise in {', '.join(user_profile['skills'][:5])}, I am confident in my ability to contribute effectively to your team.

I look forward to discussing how my skills align with your needs.

Best regards,
{user_profile['full_name']}"""

# Keep old function for backward compatibility
async def parse_cv_with_claude(file_bytes: bytes, filename: str, content_type: str) -> dict:
    return parse_cv_simple(file_bytes, filename)
