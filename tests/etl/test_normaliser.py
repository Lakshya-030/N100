import pytest
from src.etl.normaliser import normalize_ticker, normalize_year

@pytest.mark.parametrize("input_ticker, expected_output", [
    ("TCS", "TCS"),
    ("tcs", "TCS"),                    
    ("   infy  ", "INFY"),              
    ("BAJAJ-AUTO", "BAJAJ-AUTO"),       
    ("bajaj-auto ", "BAJAJ-AUTO"),      
    ("M&M", "M&M"),                     
    (" m&m ", "M&M"),
    ("HDFCBANK", "HDFCBANK"),           
    ("hdfcbank", "HDFCBANK"),
    ("RELIANCE", "RELIANCE"),          
    ("reliance", "RELIANCE"),
    ("WIPRO", "WIPRO"),
    ("wipro", "WIPRO"),
    (None, "MISSING"),                  
    ("", "MISSING"),                    
    ("   ", "MISSING"),                 
])
def test_ticker_normalization(input_ticker, expected_output):
    assert normalize_ticker(input_ticker) == expected_output


@pytest.mark.parametrize("input_year, expected_output", [
    ("2023-03", "2023-03"),             
    ("2022-12", "2022-12"),             
    ("2024-06", "2024-06"),             
    
    (2025, "2025-03"),                  
    ("2025", "2025-03"),                
    (2010, "2010-03"),                 
    (2024, "2024-03"),
    
    ("FY24", "2024-03"),                
    ("fy23", "2023-03"),                
    ("FY15", "2015-03"),
    ("FY2026", "2026-03"),              
    

    ("Mar-23", "2023-03"),              
    ("Mar 23", "2023-03"),              
    ("Dec-22", "2022-12"),              
    ("Jun-23", "2023-06"),              
    

    ("Mar 2024", "2024-03"),
    ("Sep 2024", "2024-09"),
    ("Dec 2012", "2012-12"),
    ("Jun 2021", "2021-06"),
    
    ("TTM", "TTM"),                    
    ("ttm", "TTM"),                     
    
    
    ("xyz", "PARSE ERROR"),             
    ("garbage", "PARSE ERROR"),
    (None, "PARSE ERROR"),              
])
def test_year_standardization(input_year, expected_output):
    assert normalize_year(input_year) == expected_output