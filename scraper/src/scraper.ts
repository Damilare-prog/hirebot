import { chromium, Browser, Page } from 'playwright';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const API_BASE = process.env.API_BASE_URL || 'http://api:8000';
const SCRAPER_API_KEY = process.env.SCRAPER_API_KEY || '';

export interface ScrapedJob {
  title: string;
  company: string;
  companyLogo?: string;
  location: string;
  isRemote: boolean;
  salaryMin?: number;
  salaryMax?: number;
  salaryCurrency: string;
  description: string;
  requirements: string[];
  tags: string[];
  source: string;
  sourceUrl: string;
  applyUrl: string;
  postedAt: string;
}

export class JobScraper {
  private browser: Browser | null = null;

  async init() {
    this.browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  async scrapeLinkedIn(filters: { keywords: string; location: string }) {
    // LinkedIn requires auth and has anti-bot measures.
    // In production: use LinkedIn Recruiter API or authenticated scraping with proxy rotation.
    // This is a simplified example.
    console.log('LinkedIn scraping would run here with authenticated session');
    return [];
  }

  async scrapeGreenhouse(company: string) {
    // Greenhouse boards are public and structured
    const page = await this.browser!.newPage();
    const jobs: ScrapedJob[] = [];

    try {
      await page.goto(`https://boards.greenhouse.io/${company}`, { waitUntil: 'networkidle' });

      const listings = await page.locator('.opening').all();
      for (const listing of listings) {
        const title = await listing.locator('a').textContent().catch(() => null);
        const href = await listing.locator('a').getAttribute('href').catch(() => null);
        const location = await listing.locator('.location').textContent().catch(() => 'Remote');

        if (title && href) {
          const isRemote = location.toLowerCase().includes('remote') || 
                          title.toLowerCase().includes('remote');

          jobs.push({
            title: title.trim(),
            company,
            location: location?.trim() || 'Remote',
            isRemote,
            salaryCurrency: 'USD',
            description: '', // Would need to visit detail page
            requirements: [],
            tags: this.extractTags(title),
            source: 'greenhouse',
            sourceUrl: href.startsWith('http') ? href : `https://boards.greenhouse.io${href}`,
            applyUrl: href.startsWith('http') ? href : `https://boards.greenhouse.io${href}`,
            postedAt: new Date().toISOString(),
          });
        }
      }
    } finally {
      await page.close();
    }

    return jobs;
  }

  async scrapeRemoteCo() {
    const page = await this.browser!.newPage();
    const jobs: ScrapedJob[] = [];

    try {
      await page.goto('https://remote.co/remote-jobs/developer/', { waitUntil: 'networkidle' });

      const listings = await page.locator('.job_listing').all();
      for (const listing of listings.slice(0, 20)) {
        const title = await listing.locator('.position h3').textContent().catch(() => null);
        const company = await listing.locator('.company').textContent().catch(() => null);
        const href = await listing.locator('a').first().getAttribute('href').catch(() => null);

        if (title && company && href) {
          jobs.push({
            title: title.trim(),
            company: company.trim(),
            location: 'Remote',
            isRemote: true,
            salaryCurrency: 'USD',
            description: '',
            requirements: [],
            tags: this.extractTags(title),
            source: 'remote_co',
            sourceUrl: href,
            applyUrl: href,
            postedAt: new Date().toISOString(),
          });
        }
      }
    } finally {
      await page.close();
    }

    return jobs;
  }

  private extractTags(title: string): string[] {
    const tagMap: Record<string, string[]> = {
      'react': ['React', 'Frontend'],
      'typescript': ['TypeScript'],
      'node': ['Node.js', 'Backend'],
      'python': ['Python', 'Backend'],
      'full-stack': ['Full-Stack'],
      'frontend': ['Frontend'],
      'backend': ['Backend'],
      'senior': ['Senior'],
      'staff': ['Staff'],
      'remote': ['Remote'],
    };

    const lower = title.toLowerCase();
    const tags: string[] = [];

    for (const [keyword, tagList] of Object.entries(tagMap)) {
      if (lower.includes(keyword)) {
        tags.push(...tagList);
      }
    }

    return [...new Set(tags)];
  }

  async pushToAPI(jobs: ScrapedJob[]) {
    const response = await axios.post(`${API_BASE}/jobs/ingest`, jobs, {
      headers: {
        'X-Scraper-Key': SCRAPER_API_KEY,
        'Content-Type': 'application/json',
      }
    });
    return response.data;
  }
}

// Auto-apply engine
export class AutoApplyEngine {
  private browser: Browser | null = null;

  async init() {
    this.browser = await chromium.launch({
      headless: false, // Set to true in production
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }

  async applyToGreenhouse(url: string, formData: Record<string, string>) {
    const page = await this.browser!.newPage();

    try {
      await page.goto(url, { waitUntil: 'networkidle' });

      // Map common form fields
      const fieldMap: Record<string, string> = {
        'first_name': formData.full_name?.split(' ')[0] || '',
        'last_name': formData.full_name?.split(' ').slice(1).join(' ') || '',
        'email': formData.email || '',
        'phone': formData.phone || '',
        'linkedin': formData.linkedin_url || '',
      };

      for (const [field, value] of Object.entries(fieldMap)) {
        if (value) {
          const locator = page.locator(`[name*="${field}"], [id*="${field}"]`).first();
          if (await locator.isVisible().catch(() => false)) {
            await locator.fill(value);
          }
        }
      }

      // Cover letter
      const coverLocator = page.locator('textarea[name*="cover"], textarea[name*="letter"]').first();
      if (await coverLocator.isVisible().catch(() => false)) {
        await coverLocator.fill(formData.cover_letter || '');
      }

      // In production: handle file upload for CV
      // In production: handle custom questions with LLM

      // DO NOT auto-submit in production without human review
      // This returns the filled form state for human confirmation

      const screenshot = await page.screenshot({ fullPage: true });
      return {
        success: true,
        screenshot: screenshot.toString('base64'),
        message: 'Form filled. Awaiting human confirmation before submit.',
      };
    } finally {
      await page.close();
    }
  }

  async applyToWorkday(url: string, formData: Record<string, string>) {
    // Workday forms are complex and dynamic
    // Requires more sophisticated field mapping and multi-page handling
    console.log('Workday apply not yet implemented');
    return { success: false, message: 'Workday automation pending' };
  }
}
