export interface TechStackMetric {
  module: string;
  engine: string;
}

export interface FutureModule {
  code: string;
  name: string;
  type: string;
}

export const TECHNICAL_STACK_METRICS: TechStackMetric[] = [
  { module: 'Client Layer Container', engine: 'React 18 / TypeScript' },
  { module: 'Build Orchestration', engine: 'Vite Pipeline' },
  { module: 'Layout Render Engine', engine: 'Tailwind CSS' },
  { module: 'Asynchronous Bridge', engine: 'Axios Client' },
  { module: 'Route Execution Layouts', engine: 'React Router DOM' },
];

export const PIPELINE_FUTURE_MODULES: FutureModule[] = [
  { code: 'BM-Ingest', name: 'Multimodal Ingestion Pipeline', type: 'High-Throughput Raw Serialization' },
  { code: 'BM-Extract', name: 'Digital Feature Signal Processing', type: 'Kinematic & Vocal Parametric Extraction' },
  { code: 'BM-Anomalies', name: 'Machine Learning Classification Layers', type: 'Unsupervised Latent Shift Identification' },
  { code: 'BM-Viz', name: 'High-Density Longitudinal Dashboards', type: 'Time-Series Vector Rendering Matrices' },
];