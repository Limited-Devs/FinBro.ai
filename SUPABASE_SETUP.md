# Supabase Integration Setup Guide

This guide will help you set up Supabase database integration for the FinBro.ai application.

## Prerequisites

1. A Supabase account and project
2. Python environment with required packages installed
3. Node.js environment for frontend

## Setup Instructions

### 1. Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and anon key from the project settings

### 2. Create Database Table

Run this SQL in your Supabase SQL editor to create the predictions table:

```sql
-- Create the predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);

-- Enable Row Level Security (optional, recommended for production)
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for now (modify based on your auth needs)
CREATE POLICY "Allow all operations for authenticated users" ON predictions
FOR ALL USING (true);

-- Or if you want to allow anonymous access for development:
CREATE POLICY "Allow all operations for everyone" ON predictions
FOR ALL USING (true);
```

### 3. Environment Configuration

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

### 4. Install Dependencies

#### Backend Dependencies
```bash
pip install supabase==2.8.1
```

#### Frontend Dependencies (already installed)
The `@supabase/supabase-js` package is already included in package.json.

### 5. Test the Integration

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

## How It Works

### Data Flow

1. **Prediction Creation**: When a user submits financial data, it's processed by ML models and saved to Supabase
2. **Data Retrieval**: The frontend fetches user data from Supabase via the backend API
3. **Fallback System**: If Supabase is unavailable, the system falls back to JSON file storage
4. **Real-time Updates**: Data is stored in real-time and immediately available for retrieval

### Database Schema

The `predictions` table stores:
- `id`: Unique identifier (UUID)
- `user_id`: User identifier (for future authentication integration)
- `timestamp`: When the prediction was made
- `input_data`: User's financial input data (JSON)
- `output_data`: ML model predictions (JSON)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

### API Endpoints

- `POST /api/predict`: Creates prediction and stores in Supabase
- `GET /api/data`: Retrieves user data from Supabase
- `POST /api/chat`: Chat functionality using latest prediction from Supabase

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check your Supabase URL and anon key
2. **Permission Errors**: Ensure RLS policies are configured correctly
3. **Data Not Appearing**: Check the Supabase logs for any errors

### Debug Mode

You can enable debug logging by checking the browser console and backend terminal for error messages.

### Fallback Behavior

If Supabase is unavailable:
- Backend falls back to JSON file storage
- Frontend falls back to local JSON file reading
- No data loss occurs during temporary outages

## Security Considerations

1. **Row Level Security**: Enable RLS for production use
2. **Authentication**: Integrate with Supabase Auth for user management
3. **API Keys**: Keep your anon key secure and consider using environment-specific keys

## Next Steps

1. **User Authentication**: Implement Supabase Auth for proper user management
2. **Real-time Updates**: Use Supabase real-time subscriptions for live updates
3. **Data Analytics**: Leverage Supabase's SQL capabilities for advanced analytics
4. **Backup Strategy**: Implement regular backups of your Supabase data

## Support

If you encounter issues:
1. Check the Supabase documentation
2. Review the application logs
3. Ensure all environment variables are correctly set
4. Test the database connection in Supabase dashboard
