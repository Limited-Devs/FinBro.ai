# Supabase Integration Setup Guide - Updated

This guide will help you set up Supabase database integration for the FinBro.ai application with the correct table schema.

## Prerequisites

1. A Supabase account and project
2. Python environment with required packages installed
3. The table structure provided by the user

## Setup Instructions

### 1. Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and anon key from the project settings

### 2. Configure Row Level Security (RLS)

The table already exists with the proper structure. Now you need to configure RLS policies.

**For development/testing purposes, disable RLS temporarily:**

```sql
-- Temporarily disable RLS for testing (NOT recommended for production)
ALTER TABLE public.predictions DISABLE ROW LEVEL SECURITY;
```

**For production use, enable RLS with proper policies:**

```sql
-- Enable RLS
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to insert their own predictions
CREATE POLICY "Users can insert their own predictions" ON public.predictions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Allow authenticated users to view their own predictions
CREATE POLICY "Users can view their own predictions" ON public.predictions
    FOR SELECT USING (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Allow authenticated users to update their own predictions
CREATE POLICY "Users can update their own predictions" ON public.predictions
    FOR UPDATE USING (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Allow authenticated users to delete their own predictions
CREATE POLICY "Users can delete their own predictions" ON public.predictions
    FOR DELETE USING (auth.uid()::text = user_id::text OR user_id IS NULL);

-- For development/testing: Allow anonymous access (REMOVE IN PRODUCTION)
-- CREATE POLICY "Allow anonymous access for testing" ON public.predictions
--     FOR ALL USING (true);
```

### 3. Environment Configuration

Your environment files should already be configured. Verify they contain:

#### Backend (.env in root directory)
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Existing configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Frontend (.env in frontend directory)
```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### 4. Test the Integration

Run the test script to verify everything is working:

```bash
python test_supabase.py
```

### 5. Running the Application

1. Start the backend server:
```bash
python run.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Use the application to create a financial prediction
4. Check your Supabase dashboard to see the data being stored

## How the Database Integration Works

### Table Schema

The existing `predictions` table has these key columns:
- Basic info: `id`, `timestamp`, `user_id`
- Financial data: `income`, `age`, `dependents`, `occupation`, etc.
- Expenses: `rent`, `loan_repayment`, `insurance`, etc.
- ML predictions: `savings_model_can_achieve`, `amount_model_recommended_savings`, etc.
- Categorical encodings: `occupation_retired`, `city_tier_tier_2`, etc.

### Data Mapping

The database service automatically:
1. **Flattens JSON data** from the application into individual table columns
2. **Reconstructs JSON data** when retrieving from the database
3. **Maintains compatibility** with the existing application structure

### Fallback System

If Supabase is unavailable:
- Backend falls back to JSON file storage
- Frontend falls back to local JSON file reading
- No data loss occurs during temporary outages

## Troubleshooting

### Row Level Security Errors

If you see errors like "new row violates row-level security policy":

1. **For development**: Disable RLS temporarily:
   ```sql
   ALTER TABLE public.predictions DISABLE ROW LEVEL SECURITY;
   ```

2. **For production**: Set up proper authentication and policies

### Connection Errors

- Verify your Supabase URL and anon key
- Check network connectivity
- Ensure the Supabase project is active

### Data Not Appearing

- Check the Supabase logs in your dashboard
- Verify the table structure matches the provided schema
- Check for any database constraints or triggers

## Next Steps

1. **Test the integration** with the provided test script
2. **Configure RLS properly** for your use case
3. **Implement user authentication** for production use
4. **Monitor performance** and optimize queries as needed

## Support

If you encounter issues:
1. Run the test script: `python test_supabase.py`
2. Check the Supabase dashboard for errors
3. Verify environment variables are set correctly
4. Check the console/terminal for detailed error messages
