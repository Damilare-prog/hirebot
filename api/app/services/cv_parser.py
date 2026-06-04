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
    
    # Extract name (first non-empty line)
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
        'azure', 'gcp', 'cloudflare', 'fastly', 'cloudfront',
        'spark', 'hadoop', 'hive', 'presto', 'databricks', 'snowflake',
        'dbt', 'airflow', 'luigi', 'prefect', 'dagster',
        'tableau', 'looker', 'metabase', 'superset', 'grafana',
        'segment', 'mixpanel', 'amplitude', 'heap', 'hotjar',
        'hubspot', 'salesforce', 'marketo', 'mailchimp', 'sendgrid',
        'stripe', 'paypal', 'square', 'braintree', 'adyen',
        'twilio', 'sendbird', 'stream', 'agora', 'daily.co',
        'opencv', 'pillow', 'tesseract', 'ffmpeg', 'gstreamer',
        'unity', 'unreal', 'godot', 'blender', 'maya', 'cinema4d',
        'solidity', 'web3', 'ethers.js', 'hardhat', 'truffle',
        'kubernetes', 'helm', 'istio', 'linkerd', 'consul', 'vault',
        'prometheus', 'thanos', 'cortex', 'loki', 'jaeger', 'zipkin',
        'elk', 'efk', 'splunk', 'datadog', 'newrelic', 'dynatrace',
        'pagerduty', 'opsgenie', 'victorops', 'xmatters',
        'sonarqube', 'snyk', 'checkmarx', 'veracode', 'burp',
        'metasploit', 'nmap', 'wireshark', 'tcpdump', 'nessus',
        'ansible', 'puppet', 'chef', 'saltstack', 'vagrant',
        'packer', 'nomad', 'consul', 'vault', 'boundary',
        'github actions', 'gitlab ci', 'jenkins', 'circleci', 'travis',
        'teamcity', 'bamboo', 'drone', 'argo', 'tekton', 'spinnaker',
        'selenium', 'cypress', 'playwright', 'puppeteer', 'webdriver',
        'appium', 'detox', 'calabash', ' EarlGrey', 'xctest',
        'junit', 'testng', 'pytest', 'mocha', 'jest', 'vitest',
        'cucumber', 'behave', 'robot framework', 'gauge',
        'locust', 'k6', 'artillery', 'gatling', 'jmeter', 'loader.io',
        'swagger', 'openapi', 'postman', 'insomnia', 'hoppscotch',
        'graphql', 'apollo', 'hasura', 'prisma', 'typegraphql',
        'trpc', 'grpc', 'protobuf', 'avro', 'thrift', 'jsonschema',
        'oauth', 'openid', 'saml', 'ldap', 'active directory',
        'jwt', 'bcrypt', 'argon2', 'scrypt', 'pbkdf2', 'rsa', 'ecdsa',
        'letsencrypt', 'certbot', 'acme', 'cloudflare ssl',
        'nginx', 'apache', 'caddy', 'traefik', 'envoy', 'haproxy',
        'varnish', 'squid', 'cloudflare', 'akamai', 'fastly',
        'rabbitmq', 'kafka', 'pulsar', 'nats', 'zeromq', 'activemq',
        'redis', 'memcached', 'etcd', 'zookeeper', 'consul',
        'minio', 'ceph', 'glusterfs', 'nfs', 'samba', 'afs',
        'terraform', 'pulumi', 'cdk', 'cloudformation', 'arm', 'bicep',
        'crossplane', 'backstage', 'port', 'opslevel', 'cortex',
        'datadog', 'newrelic', 'dynatrace', 'appdynamics', 'instana',
        'honeycomb', 'lightstep', 'signalfx', 'splunk', 'elastic',
        'grafana', 'prometheus', 'thanos', 'cortex', 'mimir',
        'loki', 'tempo', 'jaeger', 'zipkin', 'opentelemetry', 'opentracing',
        'sentry', 'bugsnag', 'rollbar', 'airbrake', 'raygun',
        'logrocket', 'fullstory', 'hotjar', 'crazy egg', 'optimizely',
        'launchdarkly', 'split', 'statsig', 'growthbook', 'unleash',
        'amplitude', 'mixpanel', 'segment', 'mparticle', 'rudderstack',
        'iterable', 'braze', 'clevertap', 'moengage', 'airship',
        'onesignal', 'firebase cloud messaging', 'aws sns', 'pusher',
        'ably', 'pubnub', 'socket.io', 'ws', 'websocket', 'sse',
        'webrtc', 'agora', 'daily.co', '100ms', 'mux', 'cloudflare stream',
        'twilio', 'sendbird', 'stream', 'getstream', 'talkjs',
        'stripe', 'paypal', 'braintree', 'adyen', 'square', 'checkout.com',
        'recurly', 'chargebee', 'zuora', 'paddle', 'lemonsqueezy',
        'plaid', 'yodlee', 'finicity', 'mx', 'truelayer', 'open banking',
        'sendgrid', 'mailgun', 'postmark', 'aws ses', 'mailchimp',
        'klaviyo', 'omnisend', 'drip', 'convertkit', 'activecampaign',
        'hubspot', 'salesforce', 'zoho', 'pipedrive', 'freshsales',
        'intercom', 'drift', 'crisp', 'tawk', 'zendesk', 'freshdesk',
        'servicenow', 'jira service desk', 'freshservice', 'manageengine',
        'notion', 'confluence', 'sharepoint', 'google workspace', 'slack',
        'microsoft teams', 'zoom', 'google meet', 'webex', 'goto',
        'asana', 'monday', 'clickup', 'trello', 'basecamp', 'notion',
        'linear', 'shortcut', 'height', 'plane', 'wekan', 'focalboard',
        'figma', 'sketch', 'adobe xd', 'invision', 'framer', 'proto.io',
        'balsamiq', 'axure', 'mockplus', 'moqups', 'whimsical', 'miro',
        'lucidchart', 'draw.io', 'excalidraw', 'tldraw', 'diagrams.net',
        'canva', 'crello', 'photopea', 'gimp', 'inkscape', 'krita',
        'blender', 'cinema4d', 'maya', '3ds max', 'zbrush', 'substance',
        'houdini', 'nuke', 'after effects', 'premiere', 'davinci resolve',
        'final cut', 'avid', 'lightworks', 'hitfilm', 'filmora',
        'audition', 'pro tools', 'logic pro', 'ableton', 'fl studio',
        'reason', 'cubase', 'studio one', 'bitwig', 'reaper', 'ardour',
        'obs', 'streamlabs', 'xsplit', 'vmix', 'wirecast', 'ecamm',
        'handbrake', 'ffmpeg', 'gstreamer', 'vlc', 'mpv', 'kodi',
        'plex', 'jellyfin', 'emby', 'serviio', 'universal media server',
        'nextcloud', 'owncloud', 'seafile', 'syncthing', 'resilio',
        'dropbox', 'google drive', 'onedrive', 'box', 'icloud',
        'aws s3', 'google cloud storage', 'azure blob', 'minio',
        'wasabi', 'backblaze b2', 'cloudflare r2', 'digitalocean spaces',
        'algolia', 'elasticsearch', 'typesense', 'meilisearch', 'sonic',
        'redisearch', 'sphinx', 'manticore', 'vespa', 'opensearch',
        'solr', 'lucene', 'bleve', 'tantivy', 'quickwit', 'paradedb',
        'postgres full text', 'mysql full text', 'mariadb full text',
        'sqlite fts', 'duckdb', 'clickhouse', 'druid', 'pinot',
        'presto', 'trino', 'drill', 'calcite', 'apache arrow',
        'pandas', 'polars', 'dask', 'modin', 'vaex', 'cuDF',
        'numpy', 'scipy', 'scikit-learn', 'xgboost', 'lightgbm', 'catboost',
        'tensorflow', 'pytorch', 'jax', 'mxnet', 'chainer', 'caffe',
        'keras', 'fastai', 'huggingface', 'transformers', 'diffusers',
        'stable diffusion', 'midjourney', 'dalle', 'gpt', 'llama',
        'langchain', 'llamaindex', 'haystack', 'semantic kernel',
        'autogen', 'crewai', 'dspy', 'guidance', 'outlines', 'instructor',
        'pydantic', 'dataclasses', 'attrs', 'marshmallow', 'cerberus',
        'voluptuous', 'schema', 'trafaret', 'valideer', 'validator-collection'
    ]
    
    skills = []
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title())
    
    # Remove duplicates and sort
    skills = sorted(list(set(skills)))
    
    # Extract years of experience
    years_match = re.search(r'(\d+)\+?\s*years?(?:\s*of)?(?:\s*experience)?', text_lower)
    years = int(years_match.group(1)) if years_match else 0
    
    # Extract job titles
    job_titles = []
    title_patterns = [
        r'(?:Senior|Junior|Lead|Principal|Staff|Chief)?\s*(?:Software|Frontend|Backend|Full-?Stack|DevOps|Data|ML|AI|Product|UI/UX|Web|Mobile|Cloud|Security|QA|Test)?\s*(?:Engineer|Developer|Designer|Manager|Architect|Scientist|Analyst|Specialist|Consultant|Director|VP|Head)',
        r'(?:Senior|Junior|Lead|Principal)?\s*(?:Developer|Engineer|Designer|Manager|Analyst)',
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
    
    # Limit job titles
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
        "writingStyle": f"Professional and detail-oriented with {years} years of experience."
    }

# Wrapper functions for compatibility
async def parse_cv_with_gemini(file_bytes: bytes, filename: str, content_type: str) -> dict:
    return parse_cv_simple(file_bytes, filename)

async def parse_cv_with_claude(file_bytes: bytes, filename: str, content_type: str) -> dict:
    return parse_cv_simple(file_bytes, filename)

async def generate_cover_letter(user_profile: dict, job: dict, writing_style: str) -> str:
    return f"""Dear Hiring Manager,

I am excited to apply for the {job.get('title', 'position')} at {job.get('company', 'your company')}. With {user_profile.get('years_experience', 0)} years of experience in {', '.join(user_profile.get('skills', [])[:5])}, I am confident I can make a valuable contribution.

I look forward to discussing this opportunity further.

Best regards,
{user_profile.get('full_name', 'Candidate')}"""
