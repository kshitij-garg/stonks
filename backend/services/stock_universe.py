"""
Stock Universe - NIFTY 50, Next 50, and Midcap 50
Complete list of ~150 stocks for comprehensive analysis
"""

# NIFTY 50 - Large Cap Blue Chips
NIFTY_50 = {
    "RELIANCE": {"name": "Reliance Industries", "sector": "Oil & Gas", "cap": "Large"},
    "TCS": {"name": "Tata Consultancy Services", "sector": "IT", "cap": "Large"},
    "HDFCBANK": {"name": "HDFC Bank", "sector": "Banking", "cap": "Large"},
    "INFY": {"name": "Infosys", "sector": "IT", "cap": "Large"},
    "ICICIBANK": {"name": "ICICI Bank", "sector": "Banking", "cap": "Large"},
    "HINDUNILVR": {"name": "Hindustan Unilever", "sector": "FMCG", "cap": "Large"},
    "SBIN": {"name": "State Bank of India", "sector": "Banking", "cap": "Large"},
    "BHARTIARTL": {"name": "Bharti Airtel", "sector": "Telecom", "cap": "Large"},
    "ITC": {"name": "ITC Limited", "sector": "FMCG", "cap": "Large"},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank", "sector": "Banking", "cap": "Large"},
    "LT": {"name": "Larsen & Toubro", "sector": "Infrastructure", "cap": "Large"},
    "AXISBANK": {"name": "Axis Bank", "sector": "Banking", "cap": "Large"},
    "BAJFINANCE": {"name": "Bajaj Finance", "sector": "Finance", "cap": "Large"},
    "ASIANPAINT": {"name": "Asian Paints", "sector": "Consumer Durables", "cap": "Large"},
    "MARUTI": {"name": "Maruti Suzuki", "sector": "Automobile", "cap": "Large"},
    "TITAN": {"name": "Titan Company", "sector": "Consumer Durables", "cap": "Large"},
    "SUNPHARMA": {"name": "Sun Pharmaceutical", "sector": "Pharma", "cap": "Large"},
    "TATAMOTORS": {"name": "Tata Motors", "sector": "Automobile", "cap": "Large"},
    "ULTRACEMCO": {"name": "UltraTech Cement", "sector": "Cement", "cap": "Large"},
    "WIPRO": {"name": "Wipro", "sector": "IT", "cap": "Large"},
    "ONGC": {"name": "Oil & Natural Gas Corp", "sector": "Oil & Gas", "cap": "Large"},
    "NTPC": {"name": "NTPC Limited", "sector": "Power", "cap": "Large"},
    "POWERGRID": {"name": "Power Grid Corp", "sector": "Power", "cap": "Large"},
    "HCLTECH": {"name": "HCL Technologies", "sector": "IT", "cap": "Large"},
    "TATASTEEL": {"name": "Tata Steel", "sector": "Metals", "cap": "Large"},
    "TECHM": {"name": "Tech Mahindra", "sector": "IT", "cap": "Large"},
    "COALINDIA": {"name": "Coal India", "sector": "Mining", "cap": "Large"},
    "BAJAJFINSV": {"name": "Bajaj Finserv", "sector": "Finance", "cap": "Large"},
    "JSWSTEEL": {"name": "JSW Steel", "sector": "Metals", "cap": "Large"},
    "INDUSINDBK": {"name": "IndusInd Bank", "sector": "Banking", "cap": "Large"},
    "SBILIFE": {"name": "SBI Life Insurance", "sector": "Insurance", "cap": "Large"},
    "HDFCLIFE": {"name": "HDFC Life Insurance", "sector": "Insurance", "cap": "Large"},
    "DIVISLAB": {"name": "Divi's Laboratories", "sector": "Pharma", "cap": "Large"},
    "DRREDDY": {"name": "Dr. Reddy's Labs", "sector": "Pharma", "cap": "Large"},
    "CIPLA": {"name": "Cipla", "sector": "Pharma", "cap": "Large"},
    "BRITANNIA": {"name": "Britannia Industries", "sector": "FMCG", "cap": "Large"},
    "EICHERMOT": {"name": "Eicher Motors", "sector": "Automobile", "cap": "Large"},
    "APOLLOHOSP": {"name": "Apollo Hospitals", "sector": "Healthcare", "cap": "Large"},
    "NESTLEIND": {"name": "Nestle India", "sector": "FMCG", "cap": "Large"},
    "BPCL": {"name": "Bharat Petroleum", "sector": "Oil & Gas", "cap": "Large"},
    "HINDALCO": {"name": "Hindalco Industries", "sector": "Metals", "cap": "Large"},
    "HEROMOTOCO": {"name": "Hero MotoCorp", "sector": "Automobile", "cap": "Large"},
    "TATACONSUM": {"name": "Tata Consumer Products", "sector": "FMCG", "cap": "Large"},
    "LTIM": {"name": "LTIMindtree", "sector": "IT", "cap": "Large"},
    "M&M": {"name": "Mahindra & Mahindra", "sector": "Automobile", "cap": "Large"},
    "ADANIENT": {"name": "Adani Enterprises", "sector": "Infrastructure", "cap": "Large"},
    "ADANIPORTS": {"name": "Adani Ports", "sector": "Infrastructure", "cap": "Large"},
    "GRASIM": {"name": "Grasim Industries", "sector": "Cement", "cap": "Large"},
    "BAJAJ-AUTO": {"name": "Bajaj Auto", "sector": "Automobile", "cap": "Large"},
}

# NIFTY Next 50 - Large Cap
NIFTY_NEXT_50 = {
    "ADANIGREEN": {"name": "Adani Green Energy", "sector": "Power", "cap": "Large"},
    "AMBUJACEM": {"name": "Ambuja Cements", "sector": "Cement", "cap": "Large"},
    "BANKBARODA": {"name": "Bank of Baroda", "sector": "Banking", "cap": "Large"},
    "BERGEPAINT": {"name": "Berger Paints", "sector": "Consumer Durables", "cap": "Large"},
    "BOSCHLTD": {"name": "Bosch", "sector": "Automobile", "cap": "Large"},
    "CANBK": {"name": "Canara Bank", "sector": "Banking", "cap": "Large"},
    "CHOLAFIN": {"name": "Cholamandalam Finance", "sector": "Finance", "cap": "Large"},
    "COLPAL": {"name": "Colgate Palmolive", "sector": "FMCG", "cap": "Large"},
    "DLF": {"name": "DLF Limited", "sector": "Real Estate", "cap": "Large"},
    "GAIL": {"name": "GAIL India", "sector": "Oil & Gas", "cap": "Large"},
    "GODREJCP": {"name": "Godrej Consumer Products", "sector": "FMCG", "cap": "Large"},
    "HAVELLS": {"name": "Havells India", "sector": "Consumer Durables", "cap": "Large"},
    "ICICIPRULI": {"name": "ICICI Prudential Life", "sector": "Insurance", "cap": "Large"},
    "INDIGO": {"name": "InterGlobe Aviation", "sector": "Aviation", "cap": "Large"},
    "IOC": {"name": "Indian Oil Corporation", "sector": "Oil & Gas", "cap": "Large"},
    "LICI": {"name": "Life Insurance Corp", "sector": "Insurance", "cap": "Large"},
    "MARICO": {"name": "Marico", "sector": "FMCG", "cap": "Large"},
    "NAUKRI": {"name": "Info Edge", "sector": "IT", "cap": "Large"},
    "PIDILITIND": {"name": "Pidilite Industries", "sector": "Chemicals", "cap": "Large"},
    "PNB": {"name": "Punjab National Bank", "sector": "Banking", "cap": "Large"},
    "SIEMENS": {"name": "Siemens", "sector": "Infrastructure", "cap": "Large"},
    "SRF": {"name": "SRF Limited", "sector": "Chemicals", "cap": "Large"},
    "TORNTPHARM": {"name": "Torrent Pharma", "sector": "Pharma", "cap": "Large"},
    "TRENT": {"name": "Trent Limited", "sector": "Retail", "cap": "Large"},
    "TVSMOTOR": {"name": "TVS Motor Company", "sector": "Automobile", "cap": "Large"},
    "VEDL": {"name": "Vedanta Limited", "sector": "Metals", "cap": "Large"},
    "ZOMATO": {"name": "Zomato", "sector": "Consumer Services", "cap": "Large"},
    "DABUR": {"name": "Dabur India", "sector": "FMCG", "cap": "Large"},
    "HAL": {"name": "Hindustan Aeronautics", "sector": "Defence", "cap": "Large"},
    "PFC": {"name": "Power Finance Corp", "sector": "Finance", "cap": "Large"},
    "RECLTD": {"name": "REC Limited", "sector": "Finance", "cap": "Large"},
    "SHREECEM": {"name": "Shree Cement", "sector": "Cement", "cap": "Large"},
    "JINDALSTEL": {"name": "Jindal Steel", "sector": "Metals", "cap": "Large"},
    "ABB": {"name": "ABB India", "sector": "Infrastructure", "cap": "Large"},
    "MCDOWELL-N": {"name": "United Spirits", "sector": "FMCG", "cap": "Large"},
}

# NIFTY Midcap 50
NIFTY_MIDCAP_50 = {
    "ALKEM": {"name": "Alkem Laboratories", "sector": "Pharma", "cap": "Mid"},
    "ASHOKLEY": {"name": "Ashok Leyland", "sector": "Automobile", "cap": "Mid"},
    "ASTRAL": {"name": "Astral Limited", "sector": "Plastics", "cap": "Mid"},
    "AUROPHARMA": {"name": "Aurobindo Pharma", "sector": "Pharma", "cap": "Mid"},
    "BANDHANBNK": {"name": "Bandhan Bank", "sector": "Banking", "cap": "Mid"},
    "BATAINDIA": {"name": "Bata India", "sector": "Retail", "cap": "Mid"},
    "BEL": {"name": "Bharat Electronics", "sector": "Defence", "cap": "Mid"},
    "BHEL": {"name": "Bharat Heavy Electricals", "sector": "Infrastructure", "cap": "Mid"},
    "BIOCON": {"name": "Biocon", "sector": "Pharma", "cap": "Mid"},
    "CANFINHOME": {"name": "Can Fin Homes", "sector": "Finance", "cap": "Mid"},
    "COFORGE": {"name": "Coforge", "sector": "IT", "cap": "Mid"},
    "CONCOR": {"name": "Container Corporation", "sector": "Logistics", "cap": "Mid"},
    "CUMMINSIND": {"name": "Cummins India", "sector": "Infrastructure", "cap": "Mid"},
    "DEEPAKNTR": {"name": "Deepak Nitrite", "sector": "Chemicals", "cap": "Mid"},
    "ESCORTS": {"name": "Escorts Kubota", "sector": "Automobile", "cap": "Mid"},
    "FEDERALBNK": {"name": "Federal Bank", "sector": "Banking", "cap": "Mid"},
    "GLAND": {"name": "Gland Pharma", "sector": "Pharma", "cap": "Mid"},
    "GMRINFRA": {"name": "GMR Airports", "sector": "Infrastructure", "cap": "Mid"},
    "GODREJPROP": {"name": "Godrej Properties", "sector": "Real Estate", "cap": "Mid"},
    "GUJGASLTD": {"name": "Gujarat Gas", "sector": "Oil & Gas", "cap": "Mid"},
    "IDFCFIRSTB": {"name": "IDFC First Bank", "sector": "Banking", "cap": "Mid"},
    "INDHOTEL": {"name": "Indian Hotels", "sector": "Hotels", "cap": "Mid"},
    "IRCTC": {"name": "IRCTC", "sector": "Consumer Services", "cap": "Mid"},
    "JUBLFOOD": {"name": "Jubilant FoodWorks", "sector": "Consumer Services", "cap": "Mid"},
    "L&TFH": {"name": "L&T Finance", "sector": "Finance", "cap": "Mid"},
    "LICHSGFIN": {"name": "LIC Housing Finance", "sector": "Finance", "cap": "Mid"},
    "LUPIN": {"name": "Lupin", "sector": "Pharma", "cap": "Mid"},
    "MANAPPURAM": {"name": "Manappuram Finance", "sector": "Finance", "cap": "Mid"},
    "MFSL": {"name": "Max Financial", "sector": "Insurance", "cap": "Mid"},
    "MOTHERSON": {"name": "Motherson Sumi", "sector": "Automobile", "cap": "Mid"},
    "MPHASIS": {"name": "Mphasis", "sector": "IT", "cap": "Mid"},
    "MRF": {"name": "MRF", "sector": "Automobile", "cap": "Mid"},
    "MUTHOOTFIN": {"name": "Muthoot Finance", "sector": "Finance", "cap": "Mid"},
    "NAM-INDIA": {"name": "Nippon Life India AMC", "sector": "Finance", "cap": "Mid"},
    "NMDC": {"name": "NMDC", "sector": "Mining", "cap": "Mid"},
    "OBEROIRLTY": {"name": "Oberoi Realty", "sector": "Real Estate", "cap": "Mid"},
    "OFSS": {"name": "Oracle Financial", "sector": "IT", "cap": "Mid"},
    "PAGEIND": {"name": "Page Industries", "sector": "Textiles", "cap": "Mid"},
    "PERSISTENT": {"name": "Persistent Systems", "sector": "IT", "cap": "Mid"},
    "PETRONET": {"name": "Petronet LNG", "sector": "Oil & Gas", "cap": "Mid"},
    "PIIND": {"name": "PI Industries", "sector": "Chemicals", "cap": "Mid"},
    "POLYCAB": {"name": "Polycab India", "sector": "Consumer Durables", "cap": "Mid"},
    "SYNGENE": {"name": "Syngene International", "sector": "Pharma", "cap": "Mid"},
    "TATACOMM": {"name": "Tata Communications", "sector": "Telecom", "cap": "Mid"},
    "TATAPOWER": {"name": "Tata Power", "sector": "Power", "cap": "Mid"},
    "THERMAX": {"name": "Thermax", "sector": "Infrastructure", "cap": "Mid"},
    "VOLTAS": {"name": "Voltas", "sector": "Consumer Durables", "cap": "Mid"},
    "ZYDUSLIFE": {"name": "Zydus Lifesciences", "sector": "Pharma", "cap": "Mid"},
}


def get_all_stocks():
    """Get complete stock universe"""
    all_stocks = {}
    all_stocks.update(NIFTY_50)
    all_stocks.update(NIFTY_NEXT_50)
    all_stocks.update(NIFTY_MIDCAP_50)
    return all_stocks


def get_stocks_by_cap(cap: str):
    """Get stocks by market cap category"""
    all_stocks = get_all_stocks()
    return {k: v for k, v in all_stocks.items() if v.get('cap') == cap}


def get_stocks_by_index(index: str):
    """Get stocks by index"""
    if index == 'nifty50':
        return NIFTY_50
    elif index == 'next50':
        return NIFTY_NEXT_50
    elif index == 'midcap50':
        return NIFTY_MIDCAP_50
    return get_all_stocks()


def get_sectors():
    """Get all unique sectors"""
    all_stocks = get_all_stocks()
    return sorted(set(v['sector'] for v in all_stocks.values()))


# Statistics
STOCK_COUNTS = {
    "nifty50": len(NIFTY_50),
    "next50": len(NIFTY_NEXT_50),
    "midcap50": len(NIFTY_MIDCAP_50),
    "total": len(NIFTY_50) + len(NIFTY_NEXT_50) + len(NIFTY_MIDCAP_50)
}


def search_stocks(query: str, limit: int = 10):
    """
    Search stocks by symbol or name with fuzzy matching
    Returns list of matching stocks sorted by relevance
    """
    if not query or len(query) < 1:
        return []
    
    query = query.upper().strip()
    all_stocks = get_all_stocks()
    results = []
    
    for symbol, info in all_stocks.items():
        name = info.get('name', '').upper()
        sector = info.get('sector', '')
        
        # Calculate relevance score
        score = 0
        
        # Exact symbol match = highest priority
        if symbol == query:
            score = 100
        # Symbol starts with query
        elif symbol.startswith(query):
            score = 80 + (10 - min(len(symbol) - len(query), 10))
        # Symbol contains query
        elif query in symbol:
            score = 50
        # Name starts with query
        elif name.startswith(query):
            score = 40
        # Name contains query
        elif query in name:
            score = 30
        # Sector matches
        elif query in sector.upper():
            score = 20
        
        if score > 0:
            results.append({
                'symbol': symbol,
                'name': info.get('name', ''),
                'sector': sector,
                'cap': info.get('cap', ''),
                'score': score
            })
    
    # Sort by score (highest first) and limit results
    results.sort(key=lambda x: (-x['score'], x['symbol']))
    return results[:limit]

