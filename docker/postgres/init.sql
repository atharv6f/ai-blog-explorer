-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Note: pgvector extension needs to be installed separately
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Create initial schema
CREATE SCHEMA IF NOT EXISTS blog;

-- Set search path
SET search_path TO blog, public;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC) WHERE published = TRUE;
CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author_id);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Insert test data
INSERT INTO users (id, email, name) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'admin@blog.local', 'Admin User')
ON CONFLICT (id) DO NOTHING;

INSERT INTO articles (slug, title, content, excerpt, published, published_at, author_id) VALUES
    ('hello-world', 'Hello World', 'Welcome to the AI-powered blog platform! This is your first article.', 'Welcome to the blog!', TRUE, CURRENT_TIMESTAMP, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'),
    ('getting-started', 'Getting Started', 'This article will help you get started with the platform.', 'Learn the basics', FALSE, NULL, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')
ON CONFLICT (slug) DO NOTHING;

-- Grant permissions (for production use)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA blog TO bloguser;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA blog TO bloguser;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA blog TO bloguser;

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Test user created: admin@blog.local';
    RAISE NOTICE 'Test articles created: hello-world, getting-started';
END $$;