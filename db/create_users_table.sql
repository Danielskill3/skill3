-- Create universities table
CREATE TABLE public.universities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(100) DEFAULT 'Denmark',
    is_custom BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create education_programs table
CREATE TABLE public.education_programs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    university_id UUID REFERENCES public.universities(id),
    name VARCHAR(255) NOT NULL,
    degree_level VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_id, name)
);

-- Create industries table
CREATE TABLE public.industries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create users table with extended profile information
CREATE TABLE public.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    cv_url TEXT,
    auth_provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(255),
    avatar_url TEXT,
    university_id UUID REFERENCES public.universities(id),
    education_program_id UUID REFERENCES public.education_programs(id),
    career_goal TEXT,
    career_path VARCHAR(50), -- 'specialist' or 'leadership'
    dream_companies TEXT[],
    work_mode_preference VARCHAR(50), -- 'hybrid', 'remote', or 'in_person'
    personality_type VARCHAR(10), -- MBTI type (e.g., 'INTJ')
    personality_test_url TEXT,
    onboarding_step INTEGER DEFAULT 1,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_sign_in TIMESTAMP WITH TIME ZONE
);

-- Create user_industries junction table for many-to-many relationship
CREATE TABLE public.user_industries (
    user_id UUID REFERENCES public.users(id),
    industry_id UUID REFERENCES public.industries(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, industry_id)
);

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.universities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.education_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_industries ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can read own data" ON public.users
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Service role can manage all user data" ON public.users
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Anyone can insert users" ON public.users
    FOR INSERT
    WITH CHECK (true);

-- Policies for universities table
CREATE POLICY "Universities are readable by everyone" ON public.universities
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can manage universities" ON public.universities
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policies for education_programs table
CREATE POLICY "Education programs are readable by everyone" ON public.education_programs
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can manage education programs" ON public.education_programs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policies for industries table
CREATE POLICY "Industries are readable by everyone" ON public.industries
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can manage industries" ON public.industries
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policies for user_industries table
CREATE POLICY "Users can manage their own industry preferences" ON public.user_industries
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage all user industries" ON public.user_industries
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert Danish universities
INSERT INTO public.universities (name) VALUES
    ('University of Copenhagen'),
    ('Technical University of Denmark'),
    ('Aarhus University'),
    ('Aalborg University'),
    ('University of Southern Denmark'),
    ('Copenhagen Business School'),
    ('IT University of Copenhagen'),
    ('Roskilde University');

-- Insert sample industries
INSERT INTO public.industries (name) VALUES
    ('Technology'),
    ('Finance'),
    ('Healthcare'),
    ('Education'),
    ('Manufacturing'),
    ('Consulting'),
    ('Energy'),
    ('Retail'),
    ('Media'),
    ('Transportation');

-- Create function to add custom university
CREATE OR REPLACE FUNCTION add_custom_university(university_name TEXT)
RETURNS UUID AS $$
DECLARE
    new_university_id UUID;
BEGIN
    INSERT INTO public.universities (name, is_custom)
    VALUES (university_name, true)
    RETURNING id INTO new_university_id;
    
    RETURN new_university_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
