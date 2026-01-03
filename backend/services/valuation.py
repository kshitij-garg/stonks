"""
Valuation Service with DCF and Hurdle Rate
Provides intrinsic value calculations, target prices, and valuation metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import yfinance as yf


def safe_float(val, default=0.0):
    """Convert to safe float"""
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except:
        return default


def calculate_dcf_value(symbol: str, eps: float, growth_rate: float = 0.10, 
                        discount_rate: float = 0.12, terminal_growth: float = 0.03,
                        years: int = 10) -> Dict:
    """
    Calculate DCF (Discounted Cash Flow) intrinsic value
    
    Args:
        symbol: Stock symbol
        eps: Earnings per share
        growth_rate: Expected annual EPS growth rate
        discount_rate: Required rate of return (hurdle rate)
        terminal_growth: Long-term growth rate after projection period
        years: Projection period in years
    
    Returns:
        Dict with DCF value, margin of safety, and assumptions
    """
    if eps <= 0:
        return {
            "intrinsic_value": 0,
            "present_value_earnings": 0,
            "terminal_value": 0,
            "margin_of_safety": 0,
            "assumptions": {
                "eps": eps,
                "growth_rate": growth_rate * 100,
                "discount_rate": discount_rate * 100,
                "terminal_growth": terminal_growth * 100,
                "years": years
            }
        }
    
    # Project future earnings
    projected_earnings = []
    current_eps = eps
    
    for year in range(1, years + 1):
        current_eps = current_eps * (1 + growth_rate)
        # Discount factor
        discount_factor = (1 + discount_rate) ** year
        present_value = current_eps / discount_factor
        projected_earnings.append(present_value)
    
    # Sum of present value of earnings
    pv_earnings = sum(projected_earnings)
    
    # Terminal value (Gordon Growth Model)
    final_eps = eps * ((1 + growth_rate) ** years)
    terminal_value = (final_eps * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    terminal_pv = terminal_value / ((1 + discount_rate) ** years)
    
    # Total intrinsic value per share
    intrinsic_value = pv_earnings + terminal_pv
    
    return {
        "intrinsic_value": round(intrinsic_value, 2),
        "present_value_earnings": round(pv_earnings, 2),
        "terminal_value": round(terminal_pv, 2),
        "assumptions": {
            "eps": round(eps, 2),
            "growth_rate": round(growth_rate * 100, 1),
            "discount_rate": round(discount_rate * 100, 1),
            "terminal_growth": round(terminal_growth * 100, 1),
            "years": years
        }
    }


def calculate_hurdle_rate(symbol: str, beta: float = 1.0, risk_free_rate: float = 0.07,
                          market_premium: float = 0.05) -> Dict:
    """
    Calculate hurdle rate using CAPM (Capital Asset Pricing Model)
    
    Hurdle Rate = Risk-Free Rate + Beta * Market Premium
    
    Args:
        symbol: Stock symbol
        beta: Stock's beta (volatility relative to market)
        risk_free_rate: Risk-free rate (Indian 10Y bond ~7%)
        market_premium: Expected market risk premium (~5%)
    
    Returns:
        Dict with hurdle rate and components
    """
    hurdle_rate = risk_free_rate + (beta * market_premium)
    
    return {
        "hurdle_rate": round(hurdle_rate * 100, 2),
        "risk_free_rate": round(risk_free_rate * 100, 2),
        "beta": round(beta, 2),
        "market_premium": round(market_premium * 100, 2),
        "interpretation": get_hurdle_interpretation(hurdle_rate)
    }


def get_hurdle_interpretation(rate: float) -> str:
    """Get interpretation of hurdle rate"""
    if rate < 0.10:
        return "Low risk, suitable for conservative investors"
    elif rate < 0.14:
        return "Moderate risk, average market return expected"
    elif rate < 0.18:
        return "Higher risk, requires above-average returns"
    else:
        return "High risk, speculative investment"


def calculate_pe_score(pe_ratio: float, sector: str = 'General') -> float:
    """
    Score PE ratio (lower PE = higher score for value investors)
    """
    if pe_ratio <= 0 or pd.isna(pe_ratio):
        return 50.0
    
    # Sector-specific PE benchmarks
    sector_pe = {
        'IT': 25, 'Banking': 15, 'FMCG': 35, 'Pharma': 25,
        'Automobile': 20, 'Oil & Gas': 12, 'Metals': 10,
        'Power': 12, 'Infrastructure': 18, 'Finance': 20,
        'Insurance': 25, 'Telecom': 15, 'Cement': 18,
        'Consumer Durables': 30, 'Healthcare': 28, 'Mining': 10,
        'Conglomerate': 20, 'General': 20
    }
    
    benchmark = sector_pe.get(sector, 20)
    
    if pe_ratio < benchmark * 0.5:
        return 90.0  # Very undervalued
    elif pe_ratio < benchmark * 0.75:
        return 75.0  # Undervalued
    elif pe_ratio < benchmark:
        return 60.0  # Fair value
    elif pe_ratio < benchmark * 1.5:
        return 40.0  # Slightly overvalued
    else:
        return 20.0  # Overvalued


def calculate_target_prices(current_price: float, df: pd.DataFrame,
                            pe_ratio: float = None, dcf_value: float = None) -> Dict:
    """Calculate buy/sell targets with DCF integration"""
    if df.empty or current_price <= 0:
        return {}
    
    # Calculate ATR for volatility-based targets
    if 'ATR' in df.columns:
        atr = safe_float(df.iloc[-1].get('ATR', current_price * 0.02))
    else:
        atr = current_price * 0.02
    
    # 52-week range
    high_52w = df['High'].max() if 'High' in df.columns else current_price * 1.2
    low_52w = df['Low'].min() if 'Low' in df.columns else current_price * 0.8
    
    # Technical-based targets
    buy_conservative = max(current_price - (2 * atr), low_52w * 0.95)
    buy_aggressive = max(current_price - (1.5 * atr), low_52w)
    sell_conservative = min(current_price + (2 * atr), high_52w * 0.95)
    sell_aggressive = min(current_price + (3 * atr), high_52w)
    
    # Incorporate DCF value if available
    if dcf_value and dcf_value > 0:
        # If DCF says stock is undervalued, adjust buy target up
        if dcf_value > current_price * 1.2:
            buy_conservative = min(buy_conservative * 1.05, current_price * 0.98)
        # If DCF says overvalued, adjust sell target down
        if dcf_value < current_price * 0.8:
            sell_conservative = max(sell_conservative * 0.95, current_price * 1.02)
    
    # Calculate upside/downside
    upside_conservative = ((sell_conservative - current_price) / current_price) * 100
    upside_aggressive = ((sell_aggressive - current_price) / current_price) * 100
    downside_conservative = ((current_price - buy_conservative) / current_price) * 100
    
    # Risk/Reward ratio
    risk_reward = upside_conservative / downside_conservative if downside_conservative > 0 else 0
    
    return {
        "buy_targets": {
            "conservative": round(buy_conservative, 2),
            "aggressive": round(buy_aggressive, 2)
        },
        "sell_targets": {
            "conservative": round(sell_conservative, 2),
            "aggressive": round(sell_aggressive, 2)
        },
        "upside_potential": {
            "conservative": round(upside_conservative, 2),
            "aggressive": round(upside_aggressive, 2)
        },
        "downside_risk": round(downside_conservative, 2),
        "risk_reward_ratio": round(risk_reward, 2),
        "recommendation": "BUY" if risk_reward >= 2 else "HOLD" if risk_reward >= 1 else "CAUTION"
    }


def get_market_cap_category(market_cap: float) -> str:
    """Categorize by market cap (in INR crores)"""
    if market_cap <= 0:
        return "Unknown"
    
    cap_in_crores = market_cap / 10000000  # Convert to crores
    
    if cap_in_crores >= 100000:
        return "Large Cap"
    elif cap_in_crores >= 20000:
        return "Mid Cap"
    elif cap_in_crores >= 5000:
        return "Small Cap"
    else:
        return "Micro Cap"


def get_valuation_status(current_price: float, dcf_value: float, pe_ratio: float,
                         sector_pe: float = 20) -> Dict:
    """Determine if stock is overvalued/undervalued with DCF"""
    factors = []
    score = 50  # Neutral
    
    # DCF-based valuation (most important)
    if dcf_value > 0:
        dcf_margin = ((dcf_value - current_price) / current_price) * 100
        if dcf_margin > 30:
            factors.append(f"DCF shows {dcf_margin:.0f}% upside")
            score += 25
        elif dcf_margin > 10:
            factors.append(f"DCF shows {dcf_margin:.0f}% upside")
            score += 15
        elif dcf_margin < -30:
            factors.append(f"DCF shows {abs(dcf_margin):.0f}% downside")
            score -= 25
        elif dcf_margin < -10:
            factors.append(f"DCF shows {abs(dcf_margin):.0f}% downside")
            score -= 15
    
    # PE-based valuation
    if pe_ratio > 0:
        pe_premium = ((pe_ratio - sector_pe) / sector_pe) * 100
        if pe_premium < -30:
            factors.append(f"PE {pe_premium:.0f}% below sector avg")
            score += 15
        elif pe_premium < -10:
            factors.append(f"PE slightly below sector avg")
            score += 8
        elif pe_premium > 50:
            factors.append(f"PE {pe_premium:.0f}% above sector avg")
            score -= 15
        elif pe_premium > 20:
            factors.append(f"PE above sector average")
            score -= 8
    
    # Determine status
    if score >= 70:
        status = "Undervalued"
    elif score >= 55:
        status = "Slightly Undervalued"
    elif score >= 45:
        status = "Fair Value"
    elif score >= 30:
        status = "Slightly Overvalued"
    else:
        status = "Overvalued"
    
    return {
        "status": status,
        "score": round(score, 2),
        "factors": factors
    }


def get_full_valuation_analysis(symbol: str, df: pd.DataFrame) -> Dict:
    """Complete valuation analysis with DCF and hurdle rate"""
    result = {
        "valuation": {"status": "Unknown", "score": 50, "factors": []},
        "market_cap_category": "Unknown",
        "market_cap": 0,
        "fundamentals": {},
        "targets": {},
        "pe_score": 50,
        "dcf": {},
        "hurdle_rate": {}
    }
    
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        if not info:
            return result
        
        current_price = safe_float(info.get('regularMarketPrice') or info.get('currentPrice') or 
                                   info.get('previousClose', 0))
        
        # Get fundamentals
        pe_ratio = safe_float(info.get('trailingPE', 0))
        pb_ratio = safe_float(info.get('priceToBook', 0))
        eps = safe_float(info.get('trailingEps', 0))
        roe = safe_float(info.get('returnOnEquity', 0)) * 100 if info.get('returnOnEquity') else 0
        market_cap = safe_float(info.get('marketCap', 0))
        beta = safe_float(info.get('beta', 1.0), 1.0)
        dividend_yield = safe_float(info.get('dividendYield', 0)) * 100 if info.get('dividendYield') else 0
        
        high_52w = safe_float(info.get('fiftyTwoWeekHigh', 0))
        low_52w = safe_float(info.get('fiftyTwoWeekLow', 0))
        
        # Get sector
        from services.stock_universe import get_all_stocks
        all_stocks = get_all_stocks()
        sector = all_stocks.get(symbol, {}).get('sector', 'General')
        
        # Calculate hurdle rate
        hurdle = calculate_hurdle_rate(symbol, beta)
        result["hurdle_rate"] = hurdle
        
        # Estimate growth rate based on ROE
        growth_rate = min(max(roe / 100 * 0.6, 0.05), 0.25)  # Retention ratio * ROE, bounded
        
        # Calculate DCF
        dcf = calculate_dcf_value(
            symbol, 
            eps, 
            growth_rate=growth_rate,
            discount_rate=hurdle['hurdle_rate'] / 100
        )
        
        # Add margin of safety
        if dcf['intrinsic_value'] > 0 and current_price > 0:
            dcf['margin_of_safety'] = round(
                ((dcf['intrinsic_value'] - current_price) / dcf['intrinsic_value']) * 100, 2
            )
            dcf['current_price'] = current_price
            dcf['valuation'] = "Undervalued" if dcf['margin_of_safety'] > 15 else \
                               "Fair Value" if dcf['margin_of_safety'] > -15 else "Overvalued"
        
        result["dcf"] = dcf
        
        # Calculate PE score
        result["pe_score"] = calculate_pe_score(pe_ratio, sector)
        
        # Calculate targets with DCF integration
        result["targets"] = calculate_target_prices(
            current_price, df, pe_ratio, dcf.get('intrinsic_value', 0)
        )
        
        # Get valuation status with DCF
        result["valuation"] = get_valuation_status(
            current_price, 
            dcf.get('intrinsic_value', 0),
            pe_ratio
        )
        
        # Market cap category
        result["market_cap_category"] = get_market_cap_category(market_cap)
        result["market_cap"] = int(market_cap)
        
        # Fundamentals
        result["fundamentals"] = {
            "pe_ratio": round(pe_ratio, 2),
            "pb_ratio": round(pb_ratio, 2),
            "eps": round(eps, 2),
            "roe": round(roe, 2),
            "dividend_yield": round(dividend_yield, 2),
            "beta": round(beta, 2),
            "52w_high": round(high_52w, 2),
            "52w_low": round(low_52w, 2),
            "52w_range_position": round(
                ((current_price - low_52w) / (high_52w - low_52w)) * 100, 2
            ) if high_52w > low_52w else 50
        }
        
    except Exception as e:
        print(f"Valuation error for {symbol}: {e}")
    
    return result
