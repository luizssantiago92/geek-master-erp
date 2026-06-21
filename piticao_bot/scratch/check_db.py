import os, sys
sys.path.append(os.getcwd())
from services.supabase_service import supabase

def check():
    res = supabase.table("produtos").select("*").limit(1).execute()
    if res.data:
        print(res.data[0].keys())
    else:
        print("No data")

if __name__ == "__main__":
    check()
