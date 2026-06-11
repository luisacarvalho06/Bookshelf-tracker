import os
from supabase import create_client

supabase = None

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if url and key:
    supabase = create_client(url, key)