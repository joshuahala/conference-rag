"""
Create a shared RAG answer cache.
=================================
Stores past questions + embeddings + GPT answers so similar
questions can skip generate-answer.

Usage:
    python scripts/06_create_answer_cache.py
"""

import json
import sys
import time

with open('config.public.json', 'r') as f:
    public_config = json.load(f)
with open('config.secret.json', 'r') as f:
    secrets = json.load(f)

SUPABASE_URL = public_config['SUPABASE_URL']
SUPABASE_SERVICE_KEY = secrets['SUPABASE_SERVICE_KEY']
SUPABASE_ACCESS_TOKEN = secrets['SUPABASE_ACCESS_TOKEN']
SUPABASE_PROJECT_REF = secrets['SUPABASE_PROJECT_REF']

schema_sql = """
CREATE TABLE IF NOT EXISTS question_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    answer TEXT NOT NULL,
    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE question_cache ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Authenticated users can read cache" ON question_cache;
CREATE POLICY "Authenticated users can read cache"
ON question_cache FOR SELECT
TO authenticated
USING (true);

DROP POLICY IF EXISTS "Authenticated users can insert cache" ON question_cache;
CREATE POLICY "Authenticated users can insert cache"
ON question_cache FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE OR REPLACE FUNCTION match_cached_questions(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.88,
  match_count int DEFAULT 1
)
RETURNS TABLE (
  id uuid,
  question text,
  answer text,
  sources jsonb,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    question_cache.id,
    question_cache.question,
    question_cache.answer,
    question_cache.sources,
    1 - (question_cache.embedding <=> query_embedding) as similarity
  FROM question_cache
  WHERE 1 - (question_cache.embedding <=> query_embedding) >= match_threshold
  ORDER BY question_cache.embedding <=> query_embedding
  LIMIT match_count;
$$;

GRANT EXECUTE ON FUNCTION match_cached_questions(vector, float, int) TO authenticated;
"""


def main():
    import requests
    from supabase import create_client

    print("Creating shared question_cache table...")
    url = f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json={"query": schema_sql})
    if resp.status_code not in (200, 201):
        print(f"Failed: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)

    print("Schema created. Verifying table...")
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    for attempt in range(5):
        try:
            result = client.table('question_cache').select('id', count='exact').limit(1).execute()
            print(f"question_cache ready. Rows: {result.count or 0}")
            return
        except Exception:
            if attempt < 4:
                time.sleep(3)
            else:
                print("Table created; PostgREST cache may still be refreshing.")
                return


if __name__ == '__main__':
    main()
