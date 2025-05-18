import sqlite3
import os
from prettytable import PrettyTable

def view_database():
    """View the contents of the summarizer database"""
    # Connect to the database
    db_path = "summarizer.db"
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {', '.join(table[0] for table in tables)}\n")
    
    # For each table, show its schema and content
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("Schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get content
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        print(f"\nContent ({len(rows)} rows):")
        if rows:
            # Create pretty table
            pt = PrettyTable()
            pt.field_names = [col[1] for col in columns]
            
            # For each row, truncate long text fields
            formatted_rows = []
            for row in rows:
                formatted_row = []
                for i, val in enumerate(row):
                    if isinstance(val, str) and len(val) > 100:
                        formatted_row.append(val[:100] + "...")
                    else:
                        formatted_row.append(val)
                formatted_rows.append(formatted_row)
                
            # Add rows to table
            for row in formatted_rows:
                pt.add_row(row)
                
            print(pt)
        else:
            print("  (No data)")
        print("\n" + "-"*80 + "\n")
    
    conn.close()

if __name__ == "__main__":
    # Install prettytable if needed
    try:
        import prettytable
    except ImportError:
        print("Installing prettytable...")
        import subprocess
        subprocess.check_call(["pip", "install", "prettytable"])
        
    view_database()
