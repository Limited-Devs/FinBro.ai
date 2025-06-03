import { createClient } from '@supabase/supabase-js'

// Environment variables for Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database service for frontend
export class SupabaseService {
  // Get all predictions for a user
  static async getUserPredictions(userId = 'default_user') {
    try {
      const { data, error } = await supabase
        .from('predictions')
        .select('*')
        .eq('user_id', userId)
        .order('timestamp', { ascending: false })

      if (error) {
        console.error('Error fetching predictions:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('Supabase error:', error)
      return null
    }
  }

  // Get the latest prediction for a user
  static async getLatestPrediction(userId = 'default_user') {
    try {
      const { data, error } = await supabase
        .from('predictions')
        .select('*')
        .eq('user_id', userId)
        .order('timestamp', { ascending: false })
        .limit(1)

      if (error) {
        console.error('Error fetching latest prediction:', error)
        return null
      }

      return data?.[0] || null
    } catch (error) {
      console.error('Supabase error:', error)
      return null
    }
  }

  // Create a new prediction
  static async createPrediction(predictionData: any, userId = 'default_user') {
    try {
      const { data, error } = await supabase
        .from('predictions')
        .insert([
          {
            user_id: userId,
            timestamp: predictionData.timestamp,
            input_data: predictionData.input,
            output_data: predictionData.output
          }
        ])
        .select()

      if (error) {
        console.error('Error creating prediction:', error)
        return null
      }

      return data?.[0] || null
    } catch (error) {
      console.error('Supabase error:', error)
      return null
    }
  }

  // Delete a prediction
  static async deletePrediction(predictionId: string) {
    try {
      const { error } = await supabase
        .from('predictions')
        .delete()
        .eq('id', predictionId)

      if (error) {
        console.error('Error deleting prediction:', error)
        return false
      }

      return true
    } catch (error) {
      console.error('Supabase error:', error)
      return false
    }
  }

  // Update a prediction
  static async updatePrediction(predictionId: string, updateData: any) {
    try {
      const { data, error } = await supabase
        .from('predictions')
        .update(updateData)
        .eq('id', predictionId)
        .select()

      if (error) {
        console.error('Error updating prediction:', error)
        return null
      }

      return data?.[0] || null
    } catch (error) {
      console.error('Supabase error:', error)
      return null
    }
  }

  // Test connection
  static async testConnection() {
    try {
      const { data, error } = await supabase
        .from('predictions')
        .select('count', { count: 'exact', head: true })

      if (error) {
        console.error('Connection test failed:', error)
        return false
      }

      return true
    } catch (error) {
      console.error('Connection test error:', error)
      return false
    }
  }
}
