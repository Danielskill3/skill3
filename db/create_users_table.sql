-- Create users table
CREATE TABLE public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    auth_provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(255),
    avatar_url TEXT,
    last_sign_in TIMESTAMP WITH TIME ZONE
);

-- Create RLS policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Policy for users to read their own data
CREATE POLICY "Users can read own data" ON public.users
    FOR SELECT
    USING (auth.uid() = id);

-- Policy for users to update their own data
CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE
    USING (auth.uid() = id);

-- Policy for service role to manage all data
CREATE POLICY "Service role can manage all data" ON public.users
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy for inserting new users (needed for registration)
CREATE POLICY "Anyone can insert users" ON public.users
    FOR INSERT
    WITH CHECK (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
