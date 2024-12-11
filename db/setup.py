# setup.py
import os
import sys
from pathlib import Path
from config import HITTRAX_CONFIG

def setup_local_db():
    """Set up the local database environment"""
    try:
        print("Starting HitTrax local database setup...")
        
        # 1. Create schema
        print("\nCreating database schema...")
        import schema
        schema.create_sqlite_schema()
        
        # 2. Run initial sync
        print("\nPerforming initial data sync...")
        from sync import sync_all, test_source_connection
        
        if test_source_connection():
            sync_all()
            print("\nSetup complete!")
            print("\nYou can now use the local database at:", 
                  Path(HITTRAX_CONFIG['sqlite_db']).absolute())
        else:
            print("\nFailed to connect to HitTrax database. Please check your connection settings.")
        
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    setup_local_db()