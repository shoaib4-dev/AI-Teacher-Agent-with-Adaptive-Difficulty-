"""
Quick script to help set up your database connection
Run: python setup_database.py
"""

from pathlib import Path
import os

def main():
    print("="*60)
    print("Database Setup Helper")
    print("="*60)
    
    # Check database folder
    database_folder = Path("database")
    if not database_folder.exists():
        print("\n[ERROR] 'database' folder not found!")
        print("Make sure you're running this from the project root.")
        return
    
    # List available databases
    db_files = list(database_folder.glob("*.db"))
    
    if not db_files:
        print("\n[INFO] No .db files found in database/ folder")
        print("Place your database file in: database/your_database.db")
        return
    
    print(f"\nFound {len(db_files)} database file(s) in database/ folder:")
    for i, db_file in enumerate(db_files, 1):
        size = db_file.stat().st_size / 1024  # KB
        print(f"  {i}. {db_file.name} ({size:.2f} KB)")
    
    # Ask which database to use
    if len(db_files) == 1:
        selected_db = db_files[0].name
        print(f"\n[INFO] Using: {selected_db}")
    else:
        print("\nWhich database do you want to use?")
        choice = input("Enter number (1-{}): ".format(len(db_files)))
        try:
            selected_db = db_files[int(choice) - 1].name
        except (ValueError, IndexError):
            print("[ERROR] Invalid choice")
            return
    
    # Update config file
    config_file = Path("src/config.py")
    if not config_file.exists():
        print(f"\n[ERROR] Config file not found: {config_file}")
        return
    
    # Read current config
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update DB_FILE
    import re
    pattern = r'DB_FILE\s*=\s*["\']([^"\']+)["\']'
    new_line = f'DB_FILE = "{selected_db}"'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_line, content)
    else:
        print("[ERROR] Could not find DB_FILE in config file")
        return
    
    # Write updated config
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n[SUCCESS] Updated src/config.py")
    print(f"Database file: {selected_db}")
    print(f"Full path: {Path('database') / selected_db}")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Start the backend: cd src && python app.py")
    print("2. Check database: python view_database.py")
    print("3. Verify tables are created automatically")
    print("="*60)

if __name__ == "__main__":
    main()

