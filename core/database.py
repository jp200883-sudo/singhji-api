from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

SUPABASE_CLIENT: Client = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"Supabase init failed: {e}")
