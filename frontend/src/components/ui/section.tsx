import React from 'react';
import { Container } from './Container';

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

export const Section: React.FC<SectionProps> = ({
  children,
  className = '',
  title,
  description,
}) => {
  return (
    <section className={`py-8 ${className}`}>
      <Container>
        {(title || description) && (
          <div className="mb-6">
            {title && <h2 className="text-2xl font-bold text-slate-900 tracking-tight">{title}</h2>}
            {description && <p className="mt-1 text-sm text-slate-600">{description}</p>}
          </div>
        )}
        {children}
      </Container>
    </section>
  );
};

export default Section;