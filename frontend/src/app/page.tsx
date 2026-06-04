'use client';

import { useState, useEffect, useCallback } from 'react';
import { IconBriefcase, IconSend, IconSettings, IconAdjustments, IconBolt } from '@tabler/icons-react';
import Sidebar from '@/components/Sidebar';
import JobCard from '@/components/JobCard';
import ApplyModal from '@/components/ApplyModal';
import { apiFetch } from '@/lib/utils';

const DEMO_JOBS = [
  { id: '1', title: 'Senior Frontend Engineer', company: 'Stripe', match_score: 94, salary_min: 140000, salary_max: 175000, posted_at: '2h ago', tags: ['React', 'TypeScript', 'Payments'], status: 'new', source_url: '#', apply_url: '#' },
  { id: '2', title: 'Full-Stack Developer', company: 'Linear', match_score: 89, salary_min: 120000, salary_max: 150000, posted_at: '5h ago', tags: ['React', 'Node.js', 'PostgreSQL'], status: 'applying', source_url: '#', apply_url: '#' },
  { id: '3', title: 'Frontend Engineer (Remote)', company: 'Vercel', match_score: 85, salary_min: 130000, salary_max: 160000, posted_at: '1d ago', tags: ['Next.js', 'TypeScript', 'AWS'], status: 'new', source_url: '#', apply_url: '#' },
  { id: '4', title: 'Software Engineer II', company: 'Notion', match_score: 78, salary_min: 115000, salary_max: 145000, posted_at: '2d ago', tags: ['React', 'Python', 'APIs'], status: 'applied', source_url: '#', apply_url: '#' },
  { id: '5', title: 'React Developer', company: 'Figma', match_score: 73, salary_min: 110000, salary_max: 135000, posted_at: '3d ago', tags: ['React', 'Figma', 'TypeScript'], status: 'new', source_url: '#', apply_url: '#' },
];

const TABS = [
  { id: 'jobs', label: 'Jobs', icon: IconBriefcase },
  { id: 'applied', label: 'Applied', icon: IconSend },
  { id: 'settings', label: 'Settings', icon: IconSettings },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('jobs');
  const [profile, setProfile] = useState<any>(null);
  const [jobs, setJobs] = useState(DEMO_JOBS);
  const [activeFilter, setActiveFilter] = useState('all');
  const [modalJob, setModalJob] = useState<any>(null);
  const [scanning, setScanning] = useState(true);
  const [stats, setStats] = useState({ found: 247, matches: 18, applied: 3, responses: 1 });

  // Simulate scanning status
  useEffect(() => {
    const interval = setInterval(() => {
      setScanning(s => !s);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleProfileUpdate = useCallback((p: any) => {
    setProfile(p);
    setStats(s => ({ ...s, matches: 18, found: 247 }));
  }, []);

  const handleApply = useCallback((jobId: string) => {
    if (!profile || !profile.id) {
      alert('Please upload your CV first!');
      return;
    }
    const job = jobs.find(j => j.id === jobId);
    if (job) setModalJob(job);
  }, [profile, jobs]);

  const handleApplied = useCallback(() => {
    setJobs(prev => prev.map(j => 
      j.id === modalJob?.id ? { ...j, status: 'applying' } : j
    ));
    setStats(s => ({ ...s, applied: s.applied + 1 }));

    // Simulate completion
    setTimeout(() => {
      setJobs(prev => prev.map(j => 
        j.id === modalJob?.id ? { ...j, status: 'applied' } : j
      ));
    }, 2000);
    setModalJob(null);
  }, [modalJob]);

  const autoApplyAll = useCallback(() => {
    if (!profile || !profile.id) {
      alert('Please upload your CV first!');
      return;
    }

    const eligible = jobs.filter(j => j.status === 'new');
    setJobs(prev => prev.map(j => 
      j.status === 'new' ? { ...j, status: 'applying' } : j
    ));

    let delay = 0;
    eligible.forEach((job, i) => {
      setTimeout(() => {
        setJobs(prev => prev.map(j => 
          j.id === job.id ? { ...j, status: 'applied' } : j
        ));
        setStats(s => ({ ...s, applied: s.applied + 1 }));
      }, 1200 + i * 600);
    });
  }, [profile, jobs]);

  const filteredJobs = jobs.filter(job => {
    if (activeFilter === '90plus') return (job.match_score || 0) >= 90;
    if (activeFilter === '100k') return (job.salary_min || 0) >= 100000;
    return true;
  });

  return (
    <div className="min-h-screen bg-surface-tertiary">
      {/* Topbar */}
      <header className="bg-white border-b border-border-tertiary px-8 flex items-center justify-between h-[52px]">
        <div className="flex items-center gap-2 text-[15px] font-medium text-text-primary">
          <span className="w-2 h-2 rounded-full bg-hirebot-green" />
          Hirebot
        </div>

        <nav className="flex gap-0.5">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] transition-colors
                  ${activeTab === tab.id 
                    ? 'bg-surface-secondary text-text-primary font-medium' 
                    : 'text-text-secondary hover:bg-surface-secondary'}`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-[13px] text-text-secondary">
            <span className={`w-2 h-2 rounded-full bg-hirebot-green ${scanning ? 'animate-pulse-dot' : ''}`} />
            {scanning ? 'Scanning now' : 'Scan complete'}
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="flex">
        <Sidebar 
          profile={profile} 
          onProfileUpdate={handleProfileUpdate}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        <main className="flex-1 p-6 overflow-hidden">
          {activeTab === 'jobs' && (
            <>
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-[15px] font-medium text-text-primary">Remote jobs for you</h1>
                  <p className="text-xs text-text-secondary mt-0.5">Posted in the last 7 days · sorted by match score</p>
                </div>
                <div className="flex gap-1.5">
                  <button className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] border border-border-secondary bg-white hover:bg-surface-secondary transition-colors">
                    <IconAdjustments className="w-4 h-4" /> Criteria ↗
                  </button>
                  <button 
                    onClick={autoApplyAll}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-[13px] bg-hirebot-green-dark text-hirebot-green-light border border-hirebot-green-dark hover:bg-hirebot-green transition-colors"
                  >
                    <IconBolt className="w-4 h-4" /> Auto-apply all
                  </button>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-4 gap-2 mb-4">
                {[
                  { label: 'Jobs found', value: stats.found, sub: 'this week' },
                  { label: 'Strong matches', value: stats.matches, sub: '≥80% fit' },
                  { label: 'Applied', value: stats.applied, sub: 'auto-filled' },
                  { label: 'Responses', value: stats.responses, sub: 'interview request' },
                ].map((stat) => (
                  <div key={stat.label} className="bg-white border border-border-tertiary rounded-md p-2.5 px-3">
                    <div className="text-[11px] text-text-secondary mb-1">{stat.label}</div>
                    <div className="text-xl font-medium text-text-primary">{stat.value}</div>
                    <div className="text-[11px] text-text-secondary mt-0.5">{stat.sub}</div>
                  </div>
                ))}
              </div>

              {/* Job list */}
              <div className="flex flex-col gap-1.5">
                {filteredJobs.map((job) => (
                  <JobCard key={job.id} job={job} onApply={handleApply} />
                ))}
              </div>
            </>
          )}

          {activeTab === 'applied' && (
            <div className="text-center py-20">
              <IconSend className="w-10 h-10 text-text-tertiary mx-auto mb-3" />
              <h2 className="text-lg font-medium text-text-primary mb-1">Applied jobs</h2>
              <p className="text-sm text-text-secondary">Track your applications and interview pipeline here.</p>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="text-center py-20">
              <IconSettings className="w-10 h-10 text-text-tertiary mx-auto mb-3" />
              <h2 className="text-lg font-medium text-text-primary mb-1">Settings</h2>
              <p className="text-sm text-text-secondary">Configure your job preferences, API keys, and automation rules.</p>
            </div>
          )}
        </main>
      </div>

      {/* Modal */}
      <ApplyModal
        isOpen={!!modalJob}
        onClose={() => setModalJob(null)}
        job={modalJob}
        profileId={profile?.id || ''}
        onApplied={handleApplied}
      />
    </div>
  );
}
