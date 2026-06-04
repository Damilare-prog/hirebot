export interface UserProfile {
  id: string;
  fullName: string;
  email: string;
  linkedInUrl?: string;
  yearsExperience: number;
  skills: string[];
  jobTitles: string[];
  education: EducationEntry[];
  writingStyle: string; // sample of user's writing for cover letter generation
  embedding?: number[]; // vector for semantic matching
  createdAt: string;
  updatedAt: string;
}

export interface EducationEntry {
  institution: string;
  degree: string;
  field?: string;
  year?: string;
}

export interface Job {
  id: string;
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
  source: 'linkedin' | 'greenhouse' | 'lever' | 'workday' | 'remote_co' | 'other';
  sourceUrl: string;
  applyUrl: string;
  postedAt: string;
  matchScore?: number;
  status: 'new' | 'applying' | 'applied' | 'interview' | 'rejected';
  embedding?: number[];
  createdAt: string;
}

export interface Application {
  id: string;
  userId: string;
  jobId: string;
  status: 'draft' | 'applying' | 'submitted' | 'confirmed' | 'rejected';
  coverLetter?: string;
  formData: Record<string, string>;
  submittedAt?: string;
  createdAt: string;
}

export interface CVParseResult {
  fullName: string;
  email: string;
  linkedInUrl?: string;
  phone?: string;
  yearsExperience: number;
  skills: string[];
  jobTitles: string[];
  education: EducationEntry[];
  writingStyle: string;
  rawText: string;
}
