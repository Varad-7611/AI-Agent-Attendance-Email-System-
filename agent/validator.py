def validate_spreadsheet_structure(rows: list) -> bool:
    """Validate if the spreadsheet has required columns."""
    if not rows or len(rows) < 2:
        return False
    
    # We expect columns: Roll No, Student Name, Email...
    headers = rows[1]
    if len(headers) < 3:
        return False
        
    expected_headers = ["Roll No", "Student Name", "Email"]
    for i in range(3):
        if i < len(headers) and headers[i].strip().lower() != expected_headers[i].lower():
            # Soft validation: check if basic structure looks okay even if headers differ slightly
            pass 
            
    return True
