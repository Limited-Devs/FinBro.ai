import { useQuery } from '@tanstack/react-query';
import { UserData, PredictionInput, PredictionOutput } from '@/types/user-data'; // Import PredictionInput and PredictionOutput
import { SupabaseService } from '@/services/supabase';
import { predictionAPI } from '@/services/api';

// Define a type for the raw prediction data from Supabase
interface SupabasePrediction {
  id: string;
  user_id: string;
  timestamp: string;
  input_data: PredictionInput; // Use PredictionInput type
  output_data: PredictionOutput; // Use PredictionOutput type
  // Add any other fields that come directly from your Supabase 'predictions' table
}

export const useUserData = () => {
  return useQuery({
    queryKey: ['userData'],
    queryFn: async (): Promise<UserData> => {
      try {
        // First try to get data from backend API (which will try Supabase then fallback to JSON)
        const backendData = await predictionAPI.getUserData();

        if (backendData && backendData.predictions && backendData.predictions.length > 0) {
          // Transform backend data to match expected format (input_data -> input, output_data -> output)
          const transformedData: UserData = {
            predictions: backendData.predictions.map((pred: { timestamp: string; input_data?: PredictionInput; input?: PredictionInput; output_data?: PredictionOutput; output?: PredictionOutput }) => ({
              timestamp: pred.timestamp,
              input: pred.input_data || pred.input,
              output: pred.output_data || pred.output
            }))
          };
          return transformedData;
        }

        // Fallback to direct Supabase call
        const supabaseData = await SupabaseService.getUserPredictions();

        if (supabaseData && supabaseData.length > 0) {
          // Transform Supabase data to match expected format
          const transformedData: UserData = { // Add type for transformedData
            predictions: supabaseData.map((pred: SupabasePrediction) => ({ // Use SupabasePrediction type
              timestamp: pred.timestamp,
              input: pred.input_data,
              output: pred.output_data
            }))
          };
          return transformedData;
        }

        // No data available from backend or Supabase
        throw new Error('No prediction data available. Please create a financial profile first.');

      } catch (error) {
        console.error('Error fetching user data:', error);
        // Let the error propagate for proper UI error handling
        // Per code design principles: no silent fallbacks
        throw error;
      }
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - shorter since we have real-time data
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2, // Retry failed requests twice
    retryDelay: 1000, // Wait 1 second between retries
  });
};
