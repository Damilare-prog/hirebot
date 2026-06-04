import json
import io
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    if PyPDF2 is None:
        raise ImportError("PyPDF2 not installed")
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    else:
        return file_bytes.decode('utf-8', errors='ignore')

def parse_cv_simple(file_bytes: bytes, filename: str) -> dict:
    text = extract_text_from_file(file_bytes, filename)
    text_lower = text.lower()
    
    # Extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else "unknown@email.com"
    
    # Extract phone
    phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    phone = phone_match.group(0) if phone_match else None
    
    # Extract LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9\-]+', text)
    linkedin = linkedin_match.group(0) if linkedin_match else None
    
    # Extract name
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    full_name = lines[0] if lines else "Unknown Name"
    
    # Extract skills
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
        'agile', 'scrum', 'jira', 'confluence', 'notion', 'slack', 'teams',
        'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin',
        'dart', 'flutter', 'react native', 'vue', 'angular', 'svelte', 'jquery',
        'bootstrap', 'sass', 'less', 'webpack', 'vite', 'rollup', 'esbuild',
        'jest', 'mocha', 'cypress', 'playwright', 'selenium', 'storybook',
        'prisma', 'sequelize', 'sqlalchemy', 'mongoose', 'typeorm',
        'firebase', 'supabase', 'heroku', 'netlify', 'vercel', 'digitalocean',
        'azure', 'gcp', 'cloudflare', 'fastly', 'cloudfront'
    ]
    
    skills = []
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title())
    
    skills = sorted(list(set(skills)))
    
    # Extract years
    years_match = re.search(r'(\d+)\+?\s*years?(?:\s*of)?(?:\s*experience)?', text_lower)
    years = int(years_match.group(1)) if years_match else 0
    
    # Extract job titles
    job_titles = []
    title_patterns = [
        r'(?:Senior|Junior|Lead|Principal|Staff|Chief)?\s*(?:Software|Frontend|Backend|Full-?Stack|DevOps|Data|ML|AI|Product|UI/UX|Web|Mobile|Cloud|Security|QA|Test)?\s*(?:Engineer|Developer|Designer|Manager|Architect|Scientist|Analyst|Specialist|Consultant|Director|VP|Head)',
    ]
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                title = ' '.join(filter(None, match))
            else:
                title = match
            if title and len(title) > 3 and title not in job_titles:
                job_titles.append(title.title())
    
    job_titles = job_titles[:5]
    
    return {
        "fullName": full_name,
        "email": email,
        "linkedInUrl": linkedin,
        "phone": phone,
        "yearsExperience": years,
        "skills": skills,
        "jobTitles": job_titles,
        "education": [],
        "writingStyle": f"Professional with {years} years experience."
    }

# Make these async to match the expected interface
async def parse_cv_with_gemini(file_bytes: bytes, filename: str, content_type: str) -> dict:
    return parse_cv_simple(file_bytes, filename)

async def parse_cv_with_claude(file_bytes: bytes, filename: str, content_type: str) -> dict:
    return parse_cv_simple(file_bytes, filename)

async def generate_cover_letter(user_profile: dict, job: dict, writing_style: str) -> str:
    return f"""Dear Hiring Manager,

I am excited to apply for the {job.get('title', 'position')} at {job.get('company', 'your company')}. With {user_profile.get('years_experience', 0)} years of experience in {', '.join(user_profile.get('skills', [])[:5])}, I am confident I can contribute.

Best regards,
{user_profile.get('full_name', 'Candidate')}"""
