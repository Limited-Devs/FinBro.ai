// src/services/api.js or api.ts
import { PredictionInput, PredictionOutput, ChatMessage, ChatResponse } from '@/types/user-data';

import { supabase } from '@/services/supabase';

// Use relative URLs - Vite proxy forwards /api to Flask backend on port 5000
const API_BASE_URL = '';

const getHeaders = async () => {
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
      // Ideally pass the token too if backend verified it:
      // headers['Authorization'] = `Bearer ${session.access_token}`;
    }
  }
  return headers;
};


export const chatAPI = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message } as ChatMessage),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || 'Failed to send chat message'}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Chat API Error:', error);

      // Check if it's a network error
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check if the backend is running.');
      }

      throw error;
    }
  },
};

export const predictionAPI = {
  predict: async (input: PredictionInput): Promise<PredictionOutput> => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers,
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || 'Failed to get prediction'}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Prediction API Error:', error);

      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please check if the backend is running.');
      }

      throw error;
    }
  },

  // Health check endpoint
  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      return response.ok;
    } catch {
      return false;
    }
  },

  // Get user data endpoint
  getUserData: async () => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/data`, {
        headers
      });
      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }
      return response.json();
    } catch (error) {
      console.error('Get User Data Error:', error);
      throw error;
    }
  },

  // Get monthly trends for charts
  getTrends: async (months: number = 6) => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/data/trends?months=${months}`, {
        headers
      });
      if (!response.ok) {
        throw new Error('Failed to fetch trends data');
      }
      return response.json();
    } catch (error) {
      console.error('Get Trends Error:', error);
      throw error;
    }
  }
};

// Onboarding status type
export interface OnboardingStatus {
  onboarding_completed: boolean;
  is_demo: boolean;
}

// Onboarding form data type (matches PredictionInput schema)
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
  // Get user onboarding status
  getStatus: async (): Promise<OnboardingStatus> => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/user/status`, { headers });

      if (!response.ok) {
        throw new Error('Failed to get onboarding status');
      }

      return response.json();
    } catch (error) {
      console.error('Get Status Error:', error);
      throw error;
    }
  },

  // Submit onboarding form
  submit: async (data: OnboardingFormData): Promise<OnboardingResponse> => {
    try {
      const headers = await getHeaders();
      const response = await fetch(`${API_BASE_URL}/api/onboarding`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to submit onboarding');
      }

      return response.json();
    } catch (error) {
      console.error('Onboarding Submit Error:', error);
      throw error;
    }
  }
};