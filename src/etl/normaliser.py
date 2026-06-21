from datetime import datetime

def normalize_ticker(ticker):
    """Standardizes company tickers safely by stripping spaces and upper-casing."""
    if ticker is None or str(ticker).strip() == "":
        return "MISSING"
    return str(ticker).strip().upper()

def normalize_year(year):
    """Converts diverse year labels into a standard YYYY-MM format."""
    raw_str = str(year).strip()
    
    # 1. Handle special markers and already-standardized strings 
    if raw_str.upper() == "TTM":
        return "TTM"
    if len(raw_str) == 7 and raw_str[4] == '-': 
        return raw_str
        
    # 2. Check for pure 4-digit financial years 
    # Indian financial years close in March, so explicitly append '-03' 
    if raw_str.isdigit() and len(raw_str) == 4:
        return f"{raw_str}-03"
        
    # 3. Use an explicit format sequence for month-based variations
    # Added '%b %Y' to fully handle formats like "Mar 2024" safely!
    for fmt in ("%b-%y", "%b %y", "%b-%Y", "%b %Y", "%B-%Y"):
        try:
            dt = datetime.strptime(raw_str, fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
            
    # 4. Handle 'FY24' or 'FY2024' style prefix strings 
    if raw_str.upper().startswith("FY"):
        import re
        digits = re.sub(r'\D', '', raw_str) # Extract numbers only
        if len(digits) == 2:
            return f"20{digits}-03"
        elif len(digits) == 4:
            return f"{digits}-03"
            
    return "PARSE ERROR"