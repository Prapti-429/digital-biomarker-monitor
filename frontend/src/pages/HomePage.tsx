import React from 'react';
import { Container } from '@/components/ui/Container';
import { Section } from '@/components/ui/Section';
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Alert } from '@/components/ui/Alert';
import { Button } from '@/components/ui/Button';
import { useHealth } from '@/hooks/useHealth';
import { TECHNICAL_STACK_METRICS, PIPELINE_FUTURE_MODULES } from '@/constants';

export const HomePage: React.FC = () => {
  const { status, timestamp, version, recheckHealth } = useHealth();

  return (
    <Container>
      <Section className="space-y-8">
        <div className="border-b border-slate-200 pb-6 flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
              Longitudinal Multimodal Signal Processing
            </h1>
            <p className="mt-2 text-base text-slate-600 max-w-3xl">
              Demonstrating architecture layouts optimized to organize, consolidate, and review non-clinical telemetry stream clusters.
            </p>
          </div>
          <div className="flex flex-col items-start md:items-end space-y-2">
            <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">
              System Release Frame: v{version || '2026.1.0'}
            </span>
            <StatusBadge status={status} />
          </div>
        </div>

        <Alert 
          variant="info"
          title="Architectural Boundary Specification Notice"
          message="This research infrastructure prototype serves solely as an exploratory processing model and architectural demonstration."
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card>
              <CardHeader>
                <h3 className="text-lg font-bold text-slate-900">Prototype Infrastructure Nodes</h3>
              </CardHeader>
              <CardBody className="space-y-4 text-sm text-slate-600 leading-relaxed">
                <div className="border border-slate-100 rounded-md bg-slate-50 p-4 font-mono text-xs text-slate-700 space-y-1.5">
                  <div>// Connection Metric Logging</div>
                  <div>Endpoint URI: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}</div>
                  <div>System Node Availability Flag: {status}</div>
                  {timestamp && <div>Last Sample Ping: {timestamp}</div>}
                </div>
              </CardBody>
              <CardFooter className="flex justify-between items-center">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={recheckHealth}
                  isLoading={status === 'LOADING'}
                >
                  Verify Channel Alignment
                </Button>
              </CardFooter>
            </Card>

            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4">Target Functional Subsystems</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {PIPELINE_FUTURE_MODULES.map((mod) => (
                  <div key={mod.code} className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm">
                    <span className="text-xs font-mono font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                      {mod.code}
                    </span>
                    <h4 className="font-semibold text-slate-900 text-sm mt-2">{mod.name}</h4>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <Card>
              <CardHeader>
                <h3 className="text-base font-bold text-slate-900">Configured Framework Engines</h3>
              </CardHeader>
              <CardBody className="p-0">
                <ul className="divide-y divide-slate-100" role="list">
                  {TECHNICAL_STACK_METRICS.map((tech) => (
                    <li key={tech.module} className="px-6 py-3.5">
                      <span className="text-xs text-slate-500 block">{tech.module}</span>
                      <span className="text-sm font-semibold text-slate-800">{tech.engine}</span>
                    </li>
                  ))}
                </ul>
              </CardBody>
            </Card>
          </div>
        </div>
      </Section>
    </Container>
  );
};

export default HomePage;