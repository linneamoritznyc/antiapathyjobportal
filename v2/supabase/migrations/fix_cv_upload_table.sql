-- ============================================================================
-- FIX: Create missing user_cv_uploads table
-- ============================================================================
-- This table is required by /api/cv/upload-and-analyze endpoint
-- It stores uploaded CV text and AI-generated recommendations
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_cv_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    cv_text TEXT NOT NULL,
    recommendations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_cv_uploads_user_id
    ON public.user_cv_uploads(user_id);

CREATE INDEX IF NOT EXISTS idx_user_cv_uploads_created_at
    ON public.user_cv_uploads(created_at DESC);

COMMENT ON TABLE public.user_cv_uploads IS
'Stores uploaded CV text from /api/cv/upload-and-analyze endpoint. Contains raw text and AI-generated job recommendations.';

-- RLS: Enable Row Level Security
ALTER TABLE public.user_cv_uploads ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own uploads
CREATE POLICY "Users can view own CV uploads"
    ON public.user_cv_uploads
    FOR SELECT
    USING (auth.uid() = user_id);

-- RLS Policy: Users can insert their own uploads
CREATE POLICY "Users can insert own CV uploads"
    ON public.user_cv_uploads
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Service role can do everything
CREATE POLICY "Service role can manage all CV uploads"
    ON public.user_cv_uploads
    FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================================================
-- DONE: Run this in Supabase SQL Editor to fix CV upload errors
-- ============================================================================
