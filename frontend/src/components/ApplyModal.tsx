'use client';

import { useState } from 'react';
import { IconSend, IconX } from '@tabler/icons-react';
import { apiFetch } from '@/lib/utils';

interface ApplyModalProps {
  isOpen: boolean;
  onClose: () => void;
  job: any;
  profileId: string;
  onApplied: () => void;
}

export default function ApplyModal({ isOpen, onClose, job, profileId, onApplied }: ApplyModalProps) {
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [coverLetter, setCoverLetter] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'preparing' | 'review'>('preparing');

  const prepare = async () => {
    if (!job) return;
    setLoading(true);
    setStep('preparing');

    try {
      const res = await apiFetch(`/applications/prepare?profile_id=${profileId}&job_id=${job.id}`, {
        method: 'POST',
      });
      setFormData(res.form_data);
      setCoverLetter(res.cover_letter);
      setStep('review');
    } catch (err) {
      // Demo fallback
      setFormData({
        full_name: 'Ada Okafor',
        email: 'ada.okafor@gmail.com',
        linkedin_url: 'linkedin.com/in/adaokafor',
        years_experience: '5 years (extracted from CV)',
      });
      setCoverLetter(`I'm excited to apply for the ${job.title} role at ${job.company}. With 5 years of experience building performant React/TypeScript interfaces at scale, I'm particularly drawn to ${job.company}'s...`);
      setStep('review');
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    setLoading(true);
    try {
      // In production: call /applications/{id}/submit
      await new Promise(r => setTimeout(r, 1500));
      onApplied();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/35 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl border border-border-tertiary p-6 w-full max-w-[480px] relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-text-tertiary hover:text-text-primary">
          <IconX className="w-4 h-4" />
        </button>

        <h2 className="text-[15px] font-medium text-text-primary mb-1">
          {step === 'preparing' ? 'Preparing application...' : 'Reviewing application'}
        </h2>
        <p className="text-xs text-text-secondary mb-4">
          {job?.company} · {job?.title}
        </p>

        {step === 'preparing' ? (
          <div className="py-8 text-center">
            <div className="w-8 h-8 border-2 border-hirebot-green border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-text-secondary">AI is generating your cover letter...</p>
            <button onClick={prepare} className="mt-4 text-xs text-hirebot-green underline">
              Skip to review (demo)
            </button>
          </div>
        ) : (
          <>
            <p className="text-xs font-medium text-text-secondary mb-2">
              AI will fill in the following from your CV:
            </p>

            <div className="space-y-2.5 mb-4">
              {Object.entries(formData).map(([key, val]) => (
                <div key={key}>
                  <label className="text-[12px] text-text-secondary mb-1 block capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <div className="text-[13px] text-text-primary bg-surface-secondary border border-border-tertiary rounded-md px-2.5 py-1.5">
                    {val}
                  </div>
                </div>
              ))}

              <div>
                <label className="text-[12px] text-text-secondary mb-1 block">
                  Cover letter (AI-generated, tailored)
                </label>
                <div className="text-[12px] text-text-primary bg-surface-secondary border border-border-tertiary rounded-md px-2.5 py-1.5 leading-relaxed max-h-[72px] overflow-hidden">
                  {coverLetter}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button 
                onClick={onClose}
                className="px-3.5 py-1.5 rounded-md text-[13px] border border-border-secondary bg-white hover:bg-surface-secondary transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={submit}
                disabled={loading}
                className="px-3.5 py-1.5 rounded-md text-[13px] bg-hirebot-green-dark text-hirebot-green-light border border-hirebot-green-dark hover:bg-hirebot-green flex items-center gap-1.5 transition-colors disabled:opacity-50"
              >
                <IconSend className="w-3.5 h-3.5" />
                {loading ? 'Submitting...' : 'Confirm & submit'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
