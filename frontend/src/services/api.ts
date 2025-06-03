// src/services/api.js or api.ts
import { PredictionInput, PredictionOutput, ChatMessage, ChatResponse } from '@/types/user-data';

// Use relative URLs since we're serving from the same port
const API_BASE_URL = '';

export const chatAPI = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
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
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
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
      const response = await fetch(`${API_BASE_URL}/api/data`);
      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }
      return response.json();
    } catch (error) {
      console.error('Get User Data Error:', error);
      throw error;
    }
  }
};