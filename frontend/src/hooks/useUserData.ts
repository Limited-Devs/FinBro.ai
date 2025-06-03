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
          return backendData;
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

        // Final fallback to local JSON file
        const response = await fetch('/user_data.json');
        if (!response.ok) {
          throw new Error('Failed to fetch user data from all sources');
        }
        const jsonData = await response.json();
        // Ensure the JSON data conforms to UserData type
        // This is a basic check; you might need more sophisticated validation
        if (jsonData && jsonData.predictions) {
            return jsonData as UserData;
        } else {
            throw new Error("Local JSON data is not in the expected UserData format");
        }
        
      } catch (error) {
        console.error('Error fetching user data:', error);
        // Last resort: try local JSON file
        try {
          const response = await fetch('/user_data.json');
          if (!response.ok) {
            // If local JSON also fails, and it's the last resort, rethrow to let react-query handle it
            throw new Error('Failed to fetch user data from local JSON fallback');
          }
          const fallbackJsonData = await response.json();
          if (fallbackJsonData && fallbackJsonData.predictions) {
            return fallbackJsonData as UserData;
          } else {
            throw new Error("Fallback local JSON data is not in the expected UserData format");
          }
        } catch (fallbackError) {
          console.error('All data sources failed:', fallbackError);
          throw fallbackError; // Ensure the promise rejects if all fallbacks fail
        }
      }
    },
    staleTime: 2 * 60 * 1000, // 2 minutes - shorter since we have real-time data
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 2, // Retry failed requests twice
    retryDelay: 1000, // Wait 1 second between retries
  });
};
