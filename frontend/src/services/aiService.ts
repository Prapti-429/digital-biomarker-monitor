import apiClient from './apiClient';

export interface AIAnalysisRequest {
  fatigue: number;
  mood_deviation: number;
  symptom_burden: number;
  voice_rms?: number;
  voice_zero_crossing_rate?: number;
  voice_pitch_hz?: number;
  voice_speech_activity?: number;
  face_motion?: number;
  face_luminance_variability?: number;
  face_blink_proxy?: number;
  source_duration_seconds: number;
}

export interface BiomarkerFeature {
  name: string;
  category: string;
  value: number;
  deviation?: number | null;
}

export interface AIAnalysisResponse {
  check_in_id: string;
  overall_score: number;
  trend: string;
  confidence: number;
  model_name: string;
  model_version: string;
  baseline_observations: number;
  explanation: string;
  features: BiomarkerFeature[];
  generated_at: string;
}

export interface AIHistoryPoint {
  check_in_id: string;
  score: number;
  trend: string;
  confidence: number;
  generated_at: string;
}

export interface AIHistoryResponse {
  items: AIHistoryPoint[];
  baseline_observations: number;
  model_name: string;
  model_version: string;
}

export const aiService = {
  async analyze(payload: AIAnalysisRequest): Promise<AIAnalysisResponse> {
    const response = await apiClient.post<AIAnalysisResponse>('/ai/analyze', payload);
    return response.data;
  },

  async latest(): Promise<AIAnalysisResponse> {
    const response = await apiClient.get<AIAnalysisResponse>('/ai/latest');
    return response.data;
  },

  async history(limit = 30): Promise<AIHistoryResponse> {
    const response = await apiClient.get<AIHistoryResponse>('/ai/history', { params: { limit } });
    return response.data;
  },
};
