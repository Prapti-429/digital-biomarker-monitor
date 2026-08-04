import React from 'react';
import { Container } from '@/components/ui/Container';
import { Section } from '@/components/ui/Section';
import { Card, CardBody } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';

export const AboutPage: React.FC = () => {
  return (
    <Container>
      <Section className="max-w-4xl mx-auto space-y-10">
        <div className="border-b border-slate-200 pb-6">
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
            System Protocols & Behavioral Specifications
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Analysis parameters governing long-term multi-modal signal consolidation within high-isolation sandbox environments.
          </p>
        </div>

        <Alert 
          variant="warning"
          title="Mandatory Non-Clinical Use Disclaimer"
          message="This system represents an exploratory architecture built exclusively to validate structural routing, visualization matrices, and service endpoints. It has not been registered, certified, or audited under medical device regulations. Do not use this code interface in active diagnostic routines or therapeutic workflows."
        />

        <div className="space-y-8 text-sm text-slate-600 leading-relaxed">
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-slate-900">Platform Research Scope</h3>
            <p>
              Modern smartphone systems, specialized wearables, and domestic sensory interfaces continually record metrics like physical acceleration vectors, vocal frequencies, and sleep patterns. These data streams represent indirect tracking parameters that can illuminate physiological changes over long periods without requiring direct clinical telemetry hardware.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
            <Card>
              <CardBody className="space-y-2">
                <h4 className="font-bold text-slate-900 text-base">Longitudinal Collection Logic</h4>
                <p className="text-xs text-slate-500">
                  Isolating single physical anomalies offers minimal value due to daily variance. True signal identification requires long-term baseline tracking over weeks and months.
                </p>
              </CardBody>
            </Card>
            <Card>
              <CardBody className="space-y-2">
                <h4 className="font-bold text-slate-900 text-base">Privacy-Isolated Design</h4>
                <p className="text-xs text-slate-500">
                  Biomarker arrays carry highly distinct signatures that present privacy challenges. This processing framework handles these metrics within secure storage domains.
                </p>
              </CardBody>
            </Card>
          </div>
        </div>
      </Section>
    </Container>
  );
};