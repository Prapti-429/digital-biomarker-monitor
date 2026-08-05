import React from 'react';
import { Link } from 'react-router-dom';
import { Container } from '../components/ui/Container';
import { Section } from '../components/ui/Section';

export const NotFoundPage: React.FC = () => {
  return (
    <Container>
      <Section>
        <div className="text-center py-16 space-y-4">
          <h1 className="text-6xl font-extrabold text-slate-300">404</h1>
          <h2 className="text-xl font-semibold text-slate-800">Page Not Found</h2>
          <p className="text-slate-500">The requested route does not exist.</p>
          <div>
            <Link
              to="/"
              className="inline-block px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Return Home
            </Link>
          </div>
        </div>
      </Section>
    </Container>
  );
};

export default NotFoundPage;