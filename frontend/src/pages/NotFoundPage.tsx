import React from 'react';
import { Link } from 'react-router-dom';
import { Container } from '@/components/ui/Container';
import { Section } from '@/components/ui/Section';

export const NotFoundPage: React.FC = () => {
  return (
    <Container>
      <Section className="min-h-[60vh] flex flex-col items-center justify-center text-center space-y-6">
        <div className="space-y-2">
          <span className="text-xs font-mono font-bold uppercase tracking-widest bg-red-50 text-red-600 px-3 py-1 rounded-full">
            Fault Code: 404 Route Unmapped
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
            Specified Endpoint Missing
          </h1>
        </div>
        <div>
          <Link
            to="/"
            className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Return to Core Console
          </Link>
        </div>
      </Section>
    </Container>
  );
};