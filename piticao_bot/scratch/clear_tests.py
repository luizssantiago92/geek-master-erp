import os, sys
sys.path.append(os.getcwd())
from services.supabase_service import supabase

print("Deletando produtos...")
resp = supabase.table('produtos').delete().ilike('nome', '[TESTE]%').execute()
print(f"Deletados: {len(resp.data)} produtos.")
