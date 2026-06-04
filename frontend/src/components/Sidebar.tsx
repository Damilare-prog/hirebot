'use client';

import { useState, useRef } from 'react';
import { IconUpload, IconFileText, IconCheck, IconWorld } from '@tabler/icons-react';
import { apiFetch } from '@/lib/utils';

interface SidebarProps {
  profile: any;
  onProfileUpdate: (p: any) => void;
  activeFilter: string;
  onFilterChange: (f: string) => void;
}

const FILTERS = [
  { id: 'all', label: 'All matches', color: '#1D9E75' },
  { id: '90plus', label: '90%+ match', color: '#5DCAA5' },
  { id: 'today', label: 'Posted today', color: '#378ADD' },
  { id: '100k', label: '$100k+', color: '#EF9F27' },
  { id: 'nocover', label: 'No cover letter', color: '#D4537E' },
];

const SOURCES = ['LinkedIn', 'Greenhouse', 'Lever', 'Workday', 'Remote.co'];

export default function Sidebar({ profile, onProfileUpdate, activeFilter, onFilterChange }: SidebarProps) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/profiles/upload-cv', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      onProfileUpdate(data.parsed);
    } catch (err) {
      console.error('Upload failed:', err);
      // For demo: simulate parsing
      onProfileUpdate({
        fullName: 'Ada Okafor',
        email: 'ada.okafor@gmail.com',
        skills: ['React', 'TypeScript', 'Node.js', 'Python', 'REST APIs', 'PostgreSQL', 'AWS', 'Figma'],
        yearsExperience: 5,
        jobTitles: ['Senior Frontend Engineer', 'Full-Stack Developer'],
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <aside className="w-[260px] bg-white border-r border-border-tertiary p-6 flex flex-col gap-6 shrink-0">
      {/* CV Upload */}
      <div>
        <h3 className="text-[11px] font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2">
          Your CV
        </h3>

        {!profile ? (
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="w-full border border-dashed border-border-secondary rounded-lg p-4 text-center 
                       hover:bg-surface-secondary transition-colors cursor-pointer bg-surface-secondary"
          >
            <IconUpload className="w-[22px] h-[22px] mx-auto text-text-tertiary mb-1.5" />
            <div className="text-xs font-medium text-text-secondary">
              {isUploading ? 'Parsing...' : 'Upload CV or portfolio'}
            </div>
            <div className="text-[11px] text-text-tertiary mt-0.5">PDF, DOCX, or URL</div>
          </button>
        ) : (
          <div className="border border-border-tertiary rounded-lg p-3 flex items-center gap-2.5 bg-surface-secondary">
            <div className="w-8 h-8 rounded-md bg-hirebot-green-light flex items-center justify-center shrink-0">
              <IconFileText className="w-4 h-4 text-hirebot-green-dark" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-text-primary truncate">Ada_Okafor_CV.pdf</div>
              <div className="text-[11px] text-text-secondary">Parsed · {profile.skills?.length || 14} skills extracted</div>
            </div>
            <IconCheck className="w-3.5 h-3.5 text-hirebot-green" />
          </div>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.txt"
          onChange={handleUpload}
          className="hidden"
        />
      </div>

      {/* Skills */}
      {profile && (
        <div>
          <h3 className="text-[11px] font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2">
            Matched skills
          </h3>
          <div className="flex flex-wrap gap-1">
            {(profile.skills || ['React', 'TypeScript', 'Node.js', 'Python', 'REST APIs', 'PostgreSQL', 'AWS', 'Figma']).map((skill: string) => (
              <span key={skill} className="text-[11px] px-2 py-0.5 rounded-full bg-surface-secondary border border-border-tertiary text-text-secondary">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div>
        <h3 className="text-[11px] font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2">
          Filter
        </h3>
        <div className="flex flex-col gap-0.5">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              onClick={() => onFilterChange(f.id)}
              className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-[13px] transition-colors text-left
                ${activeFilter === f.id 
                  ? 'bg-surface-secondary text-text-primary font-medium' 
                  : 'text-text-secondary hover:bg-surface-secondary'}`}
            >
              <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: f.color }} />
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div>
        <h3 className="text-[11px] font-medium text-text-tertiary uppercase tracking-wider mb-2 px-2">
          Sources
        </h3>
        <div className="flex flex-col gap-0.5">
          {SOURCES.map((source) => (
            <div key={source} className="flex items-center justify-between px-2 py-1 text-[12px] text-text-secondary">
              <span>{source}</span>
              <span className="text-hirebot-green text-xs">✓</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
