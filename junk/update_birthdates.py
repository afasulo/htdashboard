import pandas as pd
import pymssql
from datetime import datetime
from config import HITTRAX_CONFIG

# Define special cases for graduation years
SPECIAL_CASES = {
    'Colton Floyd': 2027,
    'Maddox Gonzales': 2027,
    'Kaiden Nerhood': 2026,
    'Wyatt Tinker': 2026,
    'Dean Ellison': 2026,
    'Aiden Mobley': 2026,
    'Everett Burdett': 2026,
    'Luke Feist': 2026,
    'Chase Qualler': 2026,
    'Edward Blanshine': 2026,
    'Damon Saavedra': 2026,
    'Abram Pine': 2026,
    'Noah Segura': 2026,
    'Hunter Easton': 2026,
    'Chris Moya': 2026,
    'Nathaniel Jaramillo': 2026,
    'Mark Scime': 2027,
    'Deegan Goldberg': 2026,
    'Ty Rector': 2026,
    'Avery Dearholt': 2026,
    'Landyn Cottone': 2027,
    'Caiden House': 2027,
    'Tas Lupo': 2027,
    'Logan Sunstrom': 2027,
    'Brayden Bustillos': 2027,
    'Chase Rivera': 2027,
    'Matthew Cook': 2027,
    'Richie Reiffenberger': 2028,
    'Brayden Palmerton': 2028,
    'Drew Jones': 2029,
    'James Tabbert': 2029,
    'Gavin Eaton': 2029,
    'Tyler Worthen': 2029,
    'Calin Rivera': 2029,
    'Aiden Koester': 2030,
    'Aaron Flores': 2030,
    'Brody Armstrong': 2030,
    'Adam Jimenez': 2023,
    'Jace Gabaldon': 2028,
    'Radley Philipbar': 2028,
    'Xavier Gonzales': 2028
}

def clean_csv_data(file_path):
    """
    Clean and prepare the CRM export data.
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Filter for only CHILD records
        df = df[df['type'] == 'CHILD']
        
        # Clean up names (remove extra spaces, standardize case)
        df['firstName'] = df['firstName'].str.strip().str.title()
        df['lastName'] = df['lastName'].str.strip().str.title()
        
        # Convert birthdate to datetime
        df['birthDate'] = pd.to_datetime(df['birthDate'])
        
        return df
        
    except Exception as e:
        print(f"Error cleaning CSV data: {str(e)}")
        return None

def calculate_grad_year(birth_date, full_name):
    """
    Calculate graduation year based on special cases first, then fallback to calculation.
    """
    # Check special cases first
    if full_name in SPECIAL_CASES:
        return SPECIAL_CASES[full_name]
    
    # Fallback to calculation
    kindergarten_start_year = birth_date.year + 5
    if birth_date.month > 9 or (birth_date.month == 9 and birth_date.day > 1):
        kindergarten_start_year += 1
        
    return kindergarten_start_year + 12

def update_hittrax_users(crm_data, dry_run=True):
    """
    Update HitTrax database with birthdates and graduation years from CRM data.
    """
    try:
        print("\nConnecting to HitTrax database...")
        conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
        cursor = conn.cursor(as_dict=True)
        
        # Get all users from HitTrax
        cursor.execute("""
            SELECT Id, FirstName, LastName, BirthDate, GraduationYear
            FROM Users
            WHERE Active = 1
        """)
        hittrax_users = cursor.fetchall()
        
        updates = []
        not_found = []
        already_correct = []
        special_case_updates = []
        
        print(f"\nProcessing {len(hittrax_users)} HitTrax users...")
        
        for user in hittrax_users:
            full_name = f"{user['FirstName']} {user['LastName']}"
            
            # Look for matching user in CRM data
            crm_match = crm_data[
                (crm_data['firstName'].str.lower() == user['FirstName'].lower()) &
                (crm_data['lastName'].str.lower() == user['LastName'].lower())
            ]
            
            if len(crm_match) == 0:
                not_found.append({
                    'name': full_name,
                    'current_birthdate': user['BirthDate'],
                    'current_grad_year': user['GraduationYear']
                })
                continue
                
            # Even if multiple matches found, use the first one
            crm_birth_date = crm_match.iloc[0]['birthDate'].date()
            
            # Convert HitTrax birthdate to date for comparison
            hittrax_birth_date = user['BirthDate'].date() if user['BirthDate'] else None
            
            # Determine if we need to update graduation year
            current_grad_year = user['GraduationYear']
            if current_grad_year == 1:
                new_grad_year = calculate_grad_year(crm_match.iloc[0]['birthDate'], full_name)
            else:
                new_grad_year = current_grad_year  # Preserve existing graduation year
            
            # Special case notification
            if full_name in SPECIAL_CASES:
                special_case_updates.append({
                    'name': full_name,
                    'grad_year': SPECIAL_CASES[full_name]
                })
            
            # Check if any updates are needed
            if hittrax_birth_date == crm_birth_date and current_grad_year == new_grad_year:
                already_correct.append({
                    'name': full_name,
                    'birthdate': crm_birth_date,
                    'grad_year': current_grad_year
                })
                continue
                
            updates.append({
                'id': user['Id'],
                'name': full_name,
                'old_birthdate': hittrax_birth_date,
                'new_birthdate': crm_birth_date,
                'old_grad_year': current_grad_year,
                'new_grad_year': new_grad_year,
                'grad_year_preserved': current_grad_year != 1,
                'is_special_case': full_name in SPECIAL_CASES
            })
            
            if len(crm_match) > 1:
                print(f"Note: Multiple matches found for {full_name} - updating all instances")
        
        # Print summary
        print("\n=== Special Cases ===")
        for case in special_case_updates:
            print(f"- {case['name']}: Using special case graduation year {case['grad_year']}")
            
        print(f"\nFound {len(updates)} users to update:")
        for update in updates:
            print(f"\n- {update['name']}:")
            print(f"  Birthdate: {update['old_birthdate']} → {update['new_birthdate']}")
            if update['grad_year_preserved']:
                print(f"  Grad Year: {update['old_grad_year']} (preserved)")
            else:
                src = "special case" if update['is_special_case'] else "calculated"
                print(f"  Grad Year: {update['old_grad_year']} → {update['new_grad_year']} ({src})")
            
        print(f"\nSkipped {len(already_correct)} users with correct information")
        print(f"Could not find {len(not_found)} users in CRM data")
        
        if not dry_run and updates:
            print("\nExecuting updates...")
            for update in updates:
                cursor.execute("""
                    UPDATE Users 
                    SET BirthDate = %s, GraduationYear = %s 
                    WHERE Id = %s
                """, (update['new_birthdate'], update['new_grad_year'], update['id']))
            conn.commit()
            print("Updates completed successfully!")
        elif updates:
            print("\nDry run - no changes made. Run with dry_run=False to execute updates.")
        else:
            print("\nNo updates needed.")
            
    except Exception as e:
        print(f"Error updating HitTrax database: {str(e)}")
        if not dry_run:
            conn.rollback()
    finally:
        conn.close()

def main(csv_file, dry_run=True):
    """
    Main function to coordinate the update process.
    """
    print("Starting user data update process...")
    
    # Load and clean CRM data
    crm_data = clean_csv_data(csv_file)
    if crm_data is None:
        print("Failed to load CRM data. Aborting.")
        return
        
    print(f"Loaded {len(crm_data)} records from CRM export")
    
    # Update HitTrax database
    update_hittrax_users(crm_data, dry_run)

if __name__ == "__main__":
    # Replace with your CSV file path
    csv_file = "crm_export.csv"
    
    # Run in dry-run mode first
    main(csv_file, dry_run=True)
    
    # Uncomment to perform actual updates:
    # main(csv_file, dry_run=False)