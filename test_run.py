from src.etl.normaliser import normalize_ticker, normalize_year

# Test the ticker normalizer
print("Ticker Test 1:", normalize_ticker("   infy  "))  # Expected: INFY
print("Ticker Test 2:", normalize_ticker(None))         # Expected: MISSING

# Test the year standardizer
print("Year Test 1:", normalize_year("Mar-23"))       # Expected: 2023-03
print("Year Test 2:", normalize_year("FY24"))         # Expected: 2024-03
print("Year Test 3:", normalize_year(2025))           # Expected: 2025-03
print("Year Test 4:", normalize_year("xyz"))          # Expected: PARSE ERROR