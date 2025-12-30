import sys
import time
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd

def get_financial_data(ticker, field_name):

    time.sleep(5)
    
    try:
        stock = yf.Ticker(ticker)
        
        if not stock.info:
            raise Exception(f"Ticker '{ticker}' not found")
        
        quarterly_data = get_quarterly_data(stock, field_name)
        annual_data = get_annual_data(stock, field_name)
        
        if not quarterly_data and not annual_data:
            raise Exception(f"Field '{field_name}' not found")
        
        html_content = create_financial_html(field_name, quarterly_data, annual_data)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = parse_financial_table(soup, field_name)
        if result:
            return result
        else:
            raise Exception(f"Field '{field_name}' not found")
        
    except Exception as e:
        raise Exception(f"Error: {e}")

def get_quarterly_data(stock, field_name):
    """TTM"""
    quarterly_sources = [
        stock.quarterly_financials,
        stock.quarterly_income_stmt,
        stock.quarterly_balance_sheet
    ]
    
    for quarterly in quarterly_sources:
        if not quarterly.empty and field_name in quarterly.index:
            last_4_quarters = quarterly.loc[field_name].head(4)
            ttm_value = last_4_quarters.sum()
            return {'ttm': ttm_value, 'quarters': last_4_quarters}
    
    return None

def get_annual_data(stock, field_name):
    """годовые данные"""
    annual_sources = [
        stock.financials,
        stock.income_stmt,
        stock.balance_sheet
    ]
    
    for annual in annual_sources:
        if not annual.empty and field_name in annual.index:
            annual_data = annual.loc[field_name].head(4)
            return annual_data
    
    return None

def create_financial_html(field_name, quarterly_data, annual_data):
    
    values = []

    if quarterly_data and 'ttm' in quarterly_data:
        ttm_value = quarterly_data['ttm'] / 1000 
        values.append(f"{ttm_value:,.0f}")

    if annual_data is not None:
        for value in annual_data:
            if pd.notna(value):
                annual_value = value / 1000  
                values.append(f"{annual_value:,.0f}")

    html = f"""
    <table class="financial-table">
        <tr>
            <td>{field_name}</td>
    """
    
    for value in values:
        html += f'<td>{value}</td>'
    
    html += "</tr></table>"
    
    return html

def parse_financial_table(soup, field_name):
    table = soup.find('table', class_='financial-table')
    if not table:
        return None
    
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            current_field = cells[0].get_text(strip=True)
            
            if field_name.lower() == current_field.lower():
                values = [current_field]
                for cell in cells[1:]:
                    values.append(cell.get_text(strip=True))
                return tuple(values)
    
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 financial.py 'MSFT' 'Total Revenue'")
        sys.exit(1)
    
    ticker = sys.argv[1]
    field_name = sys.argv[2]
    
    try:
        result = get_financial_data(ticker, field_name)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
