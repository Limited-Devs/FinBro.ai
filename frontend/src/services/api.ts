import { PredictionInput, PredictionOutput, ChatMessage, ChatResponse } from '@/types/user-data';
import { supabase } from '@/services/supabase';

const API_BASE_URL = '';

const getHeaders = async (): Promise<Record<string, string>> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const isDemo = localStorage.getItem('finbro_demo_mode') === 'true';
  if (isDemo) {
    headers['X-Demo-Mode'] = 'true';
    headers['X-User-ID'] = 'demo';
  } else {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.user?.id) {
      headers['X-User-ID'] = session.user.id;
    }
  }
  return headers;
};

async function apiRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = await getHeaders();

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText || 'Request failed'}`);
  }

  return response.json();
}

export const chatAPI = {
  sendMessage: (message: string): Promise<ChatResponse> =>
    apiRequest('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message } as ChatMessage),
    }),
};

export const predictionAPI = {
  predict: (input: PredictionInput): Promise<PredictionOutput> =>
    apiRequest('/api/predict', {
      method: 'POST',
      body: JSON.stringify(input),
    }),

  healthCheck: async (): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      return response.ok;
    } catch {
      return false;
    }
  },

  getUserData: (): Promise<any> =>
    apiRequest('/api/data'),

  getTrends: (months: number = 6): Promise<any> =>
    apiRequest(`/api/data/trends?months=${months}`),
};

export interface OnboardingStatus {
  onboarding_completed: boolean;
  is_demo: boolean;
}

export interface OnboardingFormData {
  Age: number;
  Dependents: number;
  Occupation: string;
  City_Tier: string;
  Income: number;
  Desired_Savings_Percentage: number;
  Rent: number;
  Loan_Repayment: number;
  Insurance: number;
  Utilities: number;
  Groceries: number;
  Transport: number;
  Eating_Out: number;
  Entertainment: number;
  Healthcare: number;
  Education: number;
  Miscellaneous: number;
}

export interface OnboardingResponse {
  success: boolean;
  onboarding_completed: boolean;
  prediction: PredictionOutput;
}

export const onboardingAPI = {
  getStatus: (): Promise<OnboardingStatus> =>
    apiRequest('/api/user/status'),

  submit: (data: OnboardingFormData): Promise<OnboardingResponse> =>
    apiRequest('/api/onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};