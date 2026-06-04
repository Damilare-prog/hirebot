export interface Job {
  id: string;
  title: string;
  company: string;
  company_logo?: string;
  location: string;
  is_remote: boolean;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  description: string;
  tags: string[];
  source: string;
  source_url: string;
  apply_url: string;
  posted_at: string;
  match_score?: number;
  status: 'new' | 'applying' | 'applied' | 'interview' | 'rejected';
}

export interface Profile {
  id: string;
  full_name: string;
  email: string;
  skills: string[];
  years_experience: number;
  job_titles: string[];
}

export interface ApplicationPrep {
  application_id: string;
  status: string;
  form_data: Record<string, string>;
  cover_letter: string;
  job: { title: string; company: string };
}
