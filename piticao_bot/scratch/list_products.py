import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import listar_produtos_teste, supabase

def main():
    prods = listar_produtos_teste()
    for p in prods:
        print(p)
        
    # Remove duplicates or ones without image if we want
    # We can also update the spiderman funko with a URL
    
if __name__ == "__main__":
    main()
