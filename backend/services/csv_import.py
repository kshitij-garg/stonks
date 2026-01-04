"""
CSV Import Service
Parse Zerodha, Groww, and other broker CSV/Excel files
"""

import pandas as pd
import io
from typing import Dict, List, Tuple
from datetime import datetime


def parse_zerodha_holdings(file_content: bytes, filename: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse Zerodha Kite holdings CSV/Excel
    
    Expected columns: Instrument, Qty., Avg. cost, LTP, Invested, Cur. val, P&L, Net chg., Day chg.
    
    Returns: (holdings_list, errors_list)
    """
    holdings = []
    errors = []
    
    try:
        # Try to parse based on file extension
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            # Try CSV with different encodings
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            except:
                df = pd.read_csv(io.BytesIO(file_content), encoding='latin-1')
        
        if df.empty:
            return [], ["File is empty"]
        
        # Normalize column names (handle variations)
        df.columns = df.columns.str.strip().str.lower().str.replace('.', '', regex=False)
        
        # Column mapping for Zerodha format
        column_map = {
            'instrument': ['instrument', 'symbol', 'tradingsymbol', 'stock'],
            'quantity': ['qty', 'quantity', 'qty.', 'shares'],
            'avg_cost': ['avg cost', 'avgcost', 'avg_cost', 'average cost', 'buy avg', 'buy price'],
            'ltp': ['ltp', 'last price', 'current price', 'cur val', 'market price'],
            'invested': ['invested', 'investment', 'buy value', 'cost'],
            'current_value': ['cur val', 'current value', 'market value'],
            'pnl': ['p&l', 'pnl', 'profit', 'profit/loss', 'gain/loss'],
            'pnl_percent': ['net chg', 'net chg.', 'pnl%', 'change%', 'returns%']
        }
        
        # Find matching columns
        def find_column(options):
            for opt in options:
                for col in df.columns:
                    if opt in col.lower():
                        return col
            return None
        
        instrument_col = find_column(column_map['instrument'])
        qty_col = find_column(column_map['quantity'])
        avg_cost_col = find_column(column_map['avg_cost'])
        ltp_col = find_column(column_map['ltp'])
        invested_col = find_column(column_map['invested'])
        pnl_col = find_column(column_map['pnl'])
        
        if not instrument_col:
            return [], ["Could not find Instrument/Symbol column"]
        
        if not qty_col:
            return [], ["Could not find Quantity column"]
        
        # Parse each row
        for idx, row in df.iterrows():
            try:
                symbol = str(row[instrument_col]).strip().upper()
                
                # Skip empty rows
                if not symbol or symbol == 'NAN' or symbol == '':
                    continue
                
                # Clean symbol (remove -BE, -EQ suffixes)
                symbol = symbol.replace('-BE', '').replace('-EQ', '').replace(' ', '')
                
                # Handle BSE/NSE variants
                if symbol.endswith('BSE') or symbol.endswith('NSE'):
                    symbol = symbol[:-3]
                
                quantity = float(row[qty_col]) if qty_col and pd.notna(row[qty_col]) else 0
                avg_cost = float(row[avg_cost_col]) if avg_cost_col and pd.notna(row[avg_cost_col]) else 0
                ltp = float(row[ltp_col]) if ltp_col and pd.notna(row[ltp_col]) else avg_cost
                invested = float(row[invested_col]) if invested_col and pd.notna(row[invested_col]) else quantity * avg_cost
                pnl = float(row[pnl_col]) if pnl_col and pd.notna(row[pnl_col]) else (ltp - avg_cost) * quantity
                
                if quantity > 0 and avg_cost > 0:
                    holdings.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'avg_price': round(avg_cost, 2),
                        'current_price': round(ltp, 2),
                        'invested_value': round(invested, 2),
                        'current_value': round(quantity * ltp, 2),
                        'pnl': round(pnl, 2),
                        'pnl_percent': round((pnl / invested) * 100, 2) if invested > 0 else 0,
                        'source': 'zerodha'
                    })
                else:
                    errors.append(f"Invalid data for {symbol}: qty={quantity}, avg={avg_cost}")
                    
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        return holdings, errors
        
    except Exception as e:
        return [], [f"Failed to parse file: {str(e)}"]


def parse_groww_holdings(file_content: bytes, filename: str) -> Tuple[List[Dict], List[str]]:
    """Parse Groww holdings format"""
    # Similar structure, different column names
    holdings = []
    errors = []
    
    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            df = pd.read_csv(io.BytesIO(file_content))
        
        df.columns = df.columns.str.strip().str.lower()
        
        # Groww specific columns
        for idx, row in df.iterrows():
            try:
                symbol = str(row.get('symbol', row.get('stock name', ''))).strip().upper()
                if not symbol:
                    continue
                
                quantity = float(row.get('quantity', row.get('qty', 0)))
                avg_cost = float(row.get('avg. buy price', row.get('buy avg', 0)))
                ltp = float(row.get('ltp', row.get('current price', avg_cost)))
                
                if quantity > 0 and avg_cost > 0:
                    holdings.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'avg_price': round(avg_cost, 2),
                        'current_price': round(ltp, 2),
                        'invested_value': round(quantity * avg_cost, 2),
                        'current_value': round(quantity * ltp, 2),
                        'pnl': round((ltp - avg_cost) * quantity, 2),
                        'pnl_percent': round(((ltp - avg_cost) / avg_cost) * 100, 2),
                        'source': 'groww'
                    })
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        return holdings, errors
        
    except Exception as e:
        return [], [f"Failed to parse Groww file: {str(e)}"]


def detect_broker_and_parse(file_content: bytes, filename: str) -> Tuple[List[Dict], List[str], str]:
    """
    Auto-detect broker format and parse
    Returns: (holdings, errors, detected_broker)
    """
    # Try Zerodha first (most common)
    holdings, errors = parse_zerodha_holdings(file_content, filename)
    if holdings:
        return holdings, errors, 'zerodha'
    
    # Try Groww
    holdings, errors = parse_groww_holdings(file_content, filename)
    if holdings:
        return holdings, errors, 'groww'
    
    return [], ["Could not detect broker format. Please ensure the file has columns: Instrument, Qty, Avg. cost"], 'unknown'
