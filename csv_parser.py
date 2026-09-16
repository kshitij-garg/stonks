import csv
import io
import re

def clean_float(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace(',', '').replace('%', '').replace('₹', '').replace('Rs.', '').replace('Rs', '').strip()
    # Handle accounting negatives like (123.45)
    if val_str.startswith('(') and val_str.endswith(')'):
        val_str = '-' + val_str[1:-1]
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def classify_instrument(name):
    clean = name.strip().upper()
    
    # 1. Check for Arbitrage / Cash / Liquid Funds
    if "ARBITRAGE" in clean or "LIQUID" in clean or "OVERNIGHT" in clean or "TREPS" in clean or "SAVINGS" in clean:
        return {
            "asset_class": "Arbitrage / Cash",
            "sub_class": "Arbitrage Debt Equivalent",
            "ticker": None,
            "is_equity": False,
            "is_etf": False,
            "is_mf": True
        }
    
    # 2. Check for Commodities (Gold / Silver)
    if "GOLD" in clean or "SILVER" in clean:
        ticker = None
        if "GOLDBEES" in clean:
            ticker = "GOLDBEES.NS"
        elif "SILVERCASE" in clean:
            ticker = "SILVERCASE.NS"
        elif "SILVERBEES" in clean:
            ticker = "SILVERBEES.NS"
        elif "AXISGOLD" in clean:
            ticker = "AXISGOLD.NS"
        elif "HDFCMFGETF" in clean:
            ticker = "HDFCMFGETF.NS"
        else:
            ticker = clean.split()[0] + ".NS"

        return {
            "asset_class": "Commodities",
            "sub_class": "Precious Metals",
            "ticker": ticker,
            "is_equity": False,
            "is_etf": True,
            "is_mf": False
        }
    
    # 3. Check for ETFs
    etf_tickers = {
        "PHARMABEES": ("PHARMABEES.NS", "Sectoral ETF - Pharma"),
        "JUNIORBEES": ("JUNIORBEES.NS", "Index ETF - Next 50"),
        "SETFNIF50": ("SETFNIF50.NS", "Index ETF - Nifty 50"),
        "NIFTYBEES": ("NIFTYBEES.NS", "Index ETF - Nifty 50"),
        "ITBEES": ("ITBEES.NS", "Sectoral ETF - IT"),
        "BANKBEES": ("BANKBEES.NS", "Sectoral ETF - Banking"),
        "AUTOBEES": ("AUTOBEES.NS", "Sectoral ETF - Auto"),
        "CPSEETF": ("CPSEETF.NS", "Index ETF - CPSE"),
        "MON100": ("MON100.NS", "Global ETF - Nasdaq 100"),
        "MAFANG": ("MAFANG.NS", "Global ETF - US Tech"),
        "HDFCNIF100": ("HDFCNIF100.NS", "Index ETF - Nifty 100"),
        "MOM30": ("MOM30.NS", "Smart Beta ETF - Momentum")
    }
    for etf_key, (ticker, sub) in etf_tickers.items():
        if etf_key in clean:
            return {
                "asset_class": "Index & Sectoral ETFs",
                "sub_class": sub,
                "ticker": ticker,
                "is_equity": False,
                "is_etf": True,
                "is_mf": False
            }
            
    # Generic ETF check
    if clean.endswith("BEES") or clean.endswith("ETF") or " ETF" in clean:
        return {
            "asset_class": "Index & Sectoral ETFs",
            "sub_class": "Sectoral / Thematic ETF",
            "ticker": clean.split()[0] + ".NS",
            "is_equity": False,
            "is_etf": True,
            "is_mf": False
        }
    
    # 4. Check for Mutual Funds
    if "FUND" in clean or "ELSS" in clean or "INDEX FUND" in clean or "DIRECT" in clean or "REGULAR" in clean:
        sub = "Flexi Cap" if "FLEXI" in clean else (
            "ELSS Tax Saver" if "ELSS" in clean else (
                "Mid Cap" if "MID" in clean else (
                    "Small Cap" if "SMALL" in clean else (
                        "Large & Mid Cap" if "LARGE" in clean else (
                            "Thematic" if "RESOURCE" in clean or "ENERGY" in clean or "INFRA" in clean else "Index Fund"
                        )
                    )
                )
            )
        )
        return {
            "asset_class": "Mutual Funds",
            "sub_class": sub,
            "ticker": None,
            "is_equity": False,
            "is_etf": False,
            "is_mf": True
        }
        
    # 5. Direct Equities (Standard NSE symbols)
    known_equities = {
        "TITAN": ("TITAN.NS", "Large Cap - Consumer Discretionary"),
        "POLYCAB": ("POLYCAB.NS", "Mid Cap - Industrials & Cables"),
        "NESTLEIND": ("NESTLEIND.NS", "Large Cap - FMCG"),
        "ARVINDFASN": ("ARVINDFASN.NS", "Small Cap - Apparel & Retail"),
        "SBIN": ("SBIN.NS", "Large Cap - Public Sector Banking"),
        "AXISBANK": ("AXISBANK.NS", "Large Cap - Private Banking"),
        "HDFCBANK": ("HDFCBANK.NS", "Large Cap - Private Banking"),
        "RELIANCE": ("RELIANCE.NS", "Large Cap - Energy & Conglomerate"),
        "TCS": ("TCS.NS", "Large Cap - IT Services"),
        "INFY": ("INFY.NS", "Large Cap - IT Services"),
        "ICICIBANK": ("ICICIBANK.NS", "Large Cap - Private Banking"),
        "ITC": ("ITC.NS", "Large Cap - FMCG"),
        "BHARTIARTL": ("BHARTIARTL.NS", "Large Cap - Telecom"),
        "LT": ("LT.NS", "Large Cap - Infrastructure"),
        "KOTAKBANK": ("KOTAKBANK.NS", "Large Cap - Private Banking"),
        "BAJFINANCE": ("BAJFINANCE.NS", "Large Cap - Financial Services"),
        "HINDUNILVR": ("HINDUNILVR.NS", "Large Cap - FMCG"),
        "TATAMOTORS": ("TATAMOTORS.NS", "Large Cap - Auto"),
        "MARUTI": ("MARUTI.NS", "Large Cap - Auto"),
        "SUNPHARMA": ("SUNPHARMA.NS", "Large Cap - Pharma"),
        "ASIANPAINT": ("ASIANPAINT.NS", "Large Cap - Paints & Chemicals")
    }
    
    ticker_clean = clean.split()[0]
    if ticker_clean in known_equities:
        tick, sub = known_equities[ticker_clean]
        return {
            "asset_class": "Direct Equities",
            "sub_class": sub,
            "ticker": tick,
            "is_equity": True,
            "is_etf": False,
            "is_mf": False
        }
    
    # Default equity fallback
    symbol = ticker_clean if not ticker_clean.endswith(".NS") else ticker_clean[:-3]
    return {
        "asset_class": "Direct Equities",
        "sub_class": "Equity Holding",
        "ticker": f"{symbol}.NS",
        "is_equity": True,
        "is_etf": False,
        "is_mf": False
    }

def find_column_index(headers, possible_names):
    for name in possible_names:
        for idx, h in enumerate(headers):
            clean_h = str(h).strip().lower().replace('.', '').replace('_', ' ')
            clean_n = name.lower()
            if clean_n == clean_h or clean_n in clean_h:
                return idx
    return None

def parse_holdings_csv(csv_text):
    """
    Parses CSV text into a structured list of holding dictionaries.
    Supports Zerodha, Groww, AngelOne, Upstox, and standard generic schemas.
    """
    holdings = []
    lines = [l for l in csv_text.splitlines() if l.strip()]
    if not lines:
        return []
        
    reader = csv.reader(lines)
    header_row = None
    
    for row in reader:
        # Check if this row looks like a header
        row_str = " ".join(row).lower()
        if any(k in row_str for k in ["instrument", "symbol", "stock", "company", "scheme", "tradingsymbol"]):
            header_row = row
            break
            
    if not header_row:
        # Fallback to first line
        reader = csv.reader(lines)
        header_row = next(reader)
        
    inst_col = find_column_index(header_row, ["instrument", "symbol", "stock", "company name", "scheme name", "tradingsymbol"])
    qty_col = find_column_index(header_row, ["qty", "quantity", "shares", "units", "total qty"])
    avg_col = find_column_index(header_row, ["avg. cost", "avg cost", "avg price", "buy avg", "buy price", "average price"])
    ltp_col = find_column_index(header_row, ["ltp", "last price", "cur. price", "current price", "nav", "market price", "cmp"])
    inv_col = find_column_index(header_row, ["invested", "buy value", "invested val", "total investment", "cost value"])
    cur_col = find_column_index(header_row, ["cur. val", "cur val", "current value", "present value", "market value"])
    pnl_col = find_column_index(header_row, ["p&l", "profit/loss", "unrealized p&l", "total p&l", "pnl"])
    net_chg_col = find_column_index(header_row, ["net chg.", "net chg", "returns %", "p&l %", "overall %", "total return %"])
    day_chg_col = find_column_index(header_row, ["day chg.", "day chg", "today's %", "1d return %", "day change %"])

    # Re-read rows after header
    reader = csv.reader(lines)
    passed_header = False
    
    for row in reader:
        if not passed_header:
            if row == header_row:
                passed_header = True
            continue
            
        if not row or len(row) <= 1:
            continue
            
        name = row[inst_col].strip() if (inst_col is not None and inst_col < len(row)) else ""
        if not name or name.lower() in ["total", "sum", "grand total"]:
            continue
            
        qty = clean_float(row[qty_col]) if (qty_col is not None and qty_col < len(row)) else 0.0
        avg_cost = clean_float(row[avg_col]) if (avg_col is not None and avg_col < len(row)) else 0.0
        ltp = clean_float(row[ltp_col]) if (ltp_col is not None and ltp_col < len(row)) else 0.0
        
        invested = clean_float(row[inv_col]) if (inv_col is not None and inv_col < len(row)) else (qty * avg_cost)
        current_val = clean_float(row[cur_col]) if (cur_col is not None and cur_col < len(row)) else (qty * ltp)
        
        pnl = clean_float(row[pnl_col]) if (pnl_col is not None and pnl_col < len(row)) else (current_val - invested)
        
        net_chg = clean_float(row[net_chg_col]) if (net_chg_col is not None and net_chg_col < len(row)) else (
            ((current_val - invested) / invested * 100) if invested > 0 else 0.0
        )
        day_chg = clean_float(row[day_chg_col]) if (day_chg_col is not None and day_chg_col < len(row)) else 0.0
        
        if qty <= 0 and current_val <= 0:
            continue
            
        classification = classify_instrument(name)
        
        holdings.append({
            "instrument": name,
            "quantity": qty,
            "avg_cost": round(avg_cost, 2),
            "ltp": round(ltp, 2),
            "invested": round(invested, 2),
            "current_value": round(current_val, 2),
            "pnl": round(pnl, 2),
            "net_chg": round(net_chg, 2),
            "day_chg": round(day_chg, 2),
            **classification
        })
        
    return holdings
