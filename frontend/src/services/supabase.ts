import { createClient } from '@supabase/supabase-js'

// Environment variables for Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database service for frontend
export class SupabaseService {
  // Get all predictions for the current or specified user
  static async getUserPredictions(userId?: string) {
    try {
      const resolvedUserId = userId ?? (await supabase.auth.getSession()).data.session?.user?.id
      if (!resolvedUserId) {
        return null
      }

      const { data, error } = await supabase
        .from('predictions')
        .select('*')
        .eq('user_id', resolvedUserId)
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
}
