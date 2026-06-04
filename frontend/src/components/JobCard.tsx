'use client';

import { IconWorld, IconClock, IconExternalLink, IconCheck, IconLoader } from '@tabler/icons-react';

interface JobCardProps {
  job: any;
  onApply: (jobId: string) => void;
}

const LOGO_COLORS: Record<string, { bg: string; text: string }> = {
  Stripe: { bg: '#E1F5EE', text: '#0F6E56' },
  Linear: { bg: '#E6F1FB', text: '#185FA5' },
  Vercel: { bg: '#F1EFE8', text: '#444441' },
  Notion: { bg: '#FAEEDA', text: '#633806' },
  Figma: { bg: '#FBEAF0', text: '#993556' },
};

export default function JobCard({ job, onApply }: JobCardProps) {
  const isApplied = job.status === 'applied' || job.status === 'confirmed';
  const isApplying = job.status === 'applying';

  const logoStyle = LOGO_COLORS[job.company] || { bg: '#F3F4F6', text: '#6B7280' };
  const initials = job.company.slice(0, 2).toUpperCase();

  const formatSalary = () => {
    if (!job.salary_min && !job.salary_max) return null;
    const min = job.salary_min ? `$${(job.salary_min / 1000).toFixed(0)}k` : '';
    const max = job.salary_max ? `$${(job.salary_max / 1000).toFixed(0)}k` : '';
    return min && max ? `${min}–${max}` : min || max;
  };

  return (
    <div className={`bg-white border rounded-lg p-4 grid grid-cols-[36px_1fr_auto] gap-3 items-start transition-all
      ${isApplying ? 'border-hirebot-green-mid border-l-[3px] border-l-hirebot-green' : ''}
      ${isApplied ? 'opacity-70 border-border-tertiary' : 'border-border-tertiary hover:border-border-secondary hover:bg-surface-secondary cursor-pointer'}`}
    >
      {/* Logo */}
      <div 
        className="w-9 h-9 rounded-md flex items-center justify-center text-[13px] font-medium shrink-0"
        style={{ background: logoStyle.bg, color: logoStyle.text }}
      >
        {initials}
      </div>

      {/* Content */}
      <div className="min-w-0">
        <h3 className="text-sm font-medium text-text-primary mb-0.5">{job.title}</h3>
        <div className="flex items-center gap-2 text-xs text-text-secondary flex-wrap mb-1.5">
          <span>{job.company}</span>
          <span className="text-border-secondary">·</span>
          <span className="flex items-center gap-0.5">
            <IconWorld className="w-3 h-3" /> Remote
          </span>
          <span className="text-border-secondary">·</span>
          <span className="flex items-center gap-0.5">
            <IconClock className="w-3 h-3" /> {job.posted_at}
          </span>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-1 mb-2">
          {isApplied && (
            <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-surface-secondary text-text-secondary flex items-center gap-1">
              <IconCheck className="w-3 h-3" /> Applied
            </span>
          )}
          {isApplying && (
            <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-hirebot-green-mid text-hirebot-green-dark flex items-center gap-1">
              <IconLoader className="w-3 h-3 animate-spin" /> Applying…
            </span>
          )}
          {!isApplied && !isApplying && (
            <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-hirebot-blue-light text-hirebot-blue">New</span>
          )}
          {formatSalary() && (
            <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-hirebot-amber-light text-hirebot-amber">{formatSalary()}</span>
          )}
          {job.tags?.map((tag: string) => (
            <span key={tag} className="text-[11px] px-1.5 py-0.5 rounded-full bg-surface-secondary text-text-secondary">
              {tag}
            </span>
          ))}
        </div>

        {/* Match bar */}
        {job.match_score !== undefined && job.match_score !== null && (
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-text-tertiary min-w-[36px]">Match</span>
            <div className="flex-1 h-1 rounded-full bg-surface-tertiary overflow-hidden max-w-[80px]">
              <div 
                className="h-full rounded-full bg-hirebot-green transition-all"
                style={{ width: `${job.match_score}%` }}
              />
            </div>
            <span className="text-[11px] text-hirebot-green-dark font-medium">{job.match_score}%</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-col items-end gap-1.5">
        <button
          onClick={() => !isApplied && !isApplying && onApply(job.id)}
          disabled={isApplied || isApplying}
          className={`px-3.5 py-1.5 rounded-md text-xs font-medium transition-colors whitespace-nowrap
            ${isApplied || isApplying 
              ? 'bg-surface-secondary text-text-secondary border border-border-tertiary cursor-default' 
              : 'bg-hirebot-green-light text-hirebot-green-dark border border-hirebot-green hover:bg-hirebot-green-mid'}`}
        >
          {isApplied ? 'Applied' : isApplying ? 'Applying…' : 'Quick apply'}
        </button>
        <a 
          href={job.source_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-[11px] text-text-tertiary flex items-center gap-0.5 hover:text-text-secondary transition-colors"
        >
          <IconExternalLink className="w-3 h-3" /> View post
        </a>
      </div>
    </div>
  );
}
