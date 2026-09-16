import time
import requests
import math
import logging

logger = logging.getLogger("analyzer")

class MarketAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.crumb = None
        self.crumb_expiry = 0
        self.cache = {}
        self.cache_ttl = 300 # 5 minutes cache
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _get_crumb(self):
        now = time.time()
        if self.crumb and now < self.crumb_expiry:
            return self.crumb
        try:
            self.session.get("https://fc.yahoo.com", headers=self.headers, timeout=5)
            r = self.session.get("https://query2.finance.yahoo.com/v1/test/getcrumb", headers=self.headers, timeout=5)
            if r.status_code == 200 and r.text:
                self.crumb = r.text.strip()
                self.crumb_expiry = now + 1800 # 30 mins
                return self.crumb
        except Exception as e:
            logger.warning(f"Failed to fetch crumb: {e}")
        return None

    def fetch_technical_data(self, ticker):
        cache_key = f"tech_{ticker}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["time"] < self.cache_ttl:
                return entry["data"]

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1d"
        try:
            r = self.session.get(url, headers=self.headers, timeout=8)
            if r.status_code != 200:
                return None
            res = r.json()
            if not res.get("chart", {}).get("result"):
                return None
            data = res["chart"]["result"][0]
            meta = data.get("meta", {})
            quotes = data.get("indicators", {}).get("quote", [{}])[0]
            
            closes = [c for c in quotes.get("close", []) if c is not None]
            highs = [h for h in quotes.get("high", []) if h is not None]
            lows = [l for l in quotes.get("low", []) if l is not None]
            volumes = [v for v in quotes.get("volume", []) if v is not None]
            
            if not closes:
                return None
                
            current_price = meta.get("regularMarketPrice", closes[-1])
            sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
            sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else current_price
            sma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else None
            
            # RSI-14
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0
            rs = avg_gain / avg_loss if avg_loss != 0 else 999
            rsi = 100 - (100 / (1 + rs))
            
            # 52w High / Low
            w52_high = meta.get("fiftyTwoWeekHigh", max(highs[-252:]) if highs else current_price)
            w52_low = meta.get("fiftyTwoWeekLow", min(lows[-252:]) if lows else current_price)
            
            pct_from_high = ((current_price - w52_high) / w52_high * 100) if w52_high else 0
            pct_from_low = ((current_price - w52_low) / w52_low * 100) if w52_low else 0
            
            # MACD (12, 26, 9)
            def calc_ema(values, period):
                k = 2 / (period + 1)
                ema = values[0]
                for val in values[1:]:
                    ema = val * k + ema * (1 - k)
                return ema
                
            ema12 = calc_ema(closes[-30:], 12) if len(closes) >= 30 else current_price
            ema26 = calc_ema(closes[-30:], 26) if len(closes) >= 30 else current_price
            macd = ema12 - ema26
            
            # Support and Resistance
            support = min(lows[-20:]) if len(lows) >= 20 else min(lows)
            resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs)
            
            # Trend determination
            if sma200 and current_price > sma50 > sma200:
                trend = "Strong Bullish"
            elif current_price > sma20:
                trend = "Bullish Uptrend"
            elif sma200 and current_price < sma200:
                trend = "Bearish Breakdown"
            else:
                trend = "Consolidation / Pullback"

            result = {
                "current_price": round(current_price, 2),
                "sma20": round(sma20, 2),
                "sma50": round(sma50, 2),
                "sma200": round(sma200, 2) if sma200 else None,
                "rsi14": round(rsi, 1),
                "macd": round(macd, 2),
                "w52_high": round(w52_high, 2),
                "w52_low": round(w52_low, 2),
                "pct_from_high": round(pct_from_high, 1),
                "pct_from_low": round(pct_from_low, 1),
                "support": round(support, 2),
                "resistance": round(resistance, 2),
                "trend": trend,
                "history_closes": closes[-60:],
                "timestamps": data.get("timestamp", [])[-60:]
            }
            self.cache[cache_key] = {"data": result, "time": time.time()}
            return result
        except Exception as e:
            logger.warning(f"Error fetching technical data for {ticker}: {e}")
            return None

    def fetch_fundamental_data(self, ticker):
        cache_key = f"fund_{ticker}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["time"] < self.cache_ttl:
                return entry["data"]

        crumb = self._get_crumb()
        crumb_param = f"&crumb={crumb}" if crumb else ""
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics,financialData,summaryDetail,recommendationTrend{crumb_param}"
        try:
            r = self.session.get(url, headers=self.headers, timeout=8)
            if r.status_code != 200:
                return None
            res = r.json()
            if not res.get("quoteSummary", {}).get("result"):
                return None
            raw = res["quoteSummary"]["result"][0]
            fin = raw.get("financialData", {})
            sum_det = raw.get("summaryDetail", {})
            stats = raw.get("defaultKeyStatistics", {})
            
            pe = sum_det.get("trailingPE", {}).get("raw")
            fwd_pe = sum_det.get("forwardPE", {}).get("raw")
            market_cap = sum_det.get("marketCap", {}).get("raw")
            market_cap_fmt = sum_det.get("marketCap", {}).get("fmt", "N/A")
            profit_margins = fin.get("profitMargins", {}).get("raw")
            gross_margins = fin.get("grossMargins", {}).get("raw")
            roe = fin.get("returnOnEquity", {}).get("raw")
            debt_to_equity = fin.get("debtToEquity", {}).get("raw")
            
            # Analyst targets
            rec_key = fin.get("recommendationKey", "hold")
            num_analysts = fin.get("numberOfAnalystOpinions", {}).get("raw", 0)
            target_mean = fin.get("targetMeanPrice", {}).get("raw")
            target_high = fin.get("targetHighPrice", {}).get("raw")
            target_low = fin.get("targetLowPrice", {}).get("raw")

            result = {
                "pe": round(pe, 1) if pe else None,
                "forward_pe": round(fwd_pe, 1) if fwd_pe else None,
                "market_cap": market_cap,
                "market_cap_fmt": market_cap_fmt,
                "profit_margins_pct": round(profit_margins * 100, 1) if profit_margins else None,
                "gross_margins_pct": round(gross_margins * 100, 1) if gross_margins else None,
                "roe_pct": round(roe * 100, 1) if roe else None,
                "debt_to_equity": round(debt_to_equity, 1) if debt_to_equity else None,
                "recommendation_key": rec_key,
                "num_analysts": num_analysts,
                "target_mean": round(target_mean, 2) if target_mean else None,
                "target_high": round(target_high, 2) if target_high else None,
                "target_low": round(target_low, 2) if target_low else None,
            }
            self.cache[cache_key] = {"data": result, "time": time.time()}
            return result
        except Exception as e:
            logger.warning(f"Error fetching fundamentals for {ticker}: {e}")
            return None

    def fetch_mf_data(self, fund_name, expected_ltp=None):
        cache_key = f"mf_{fund_name}_{expected_ltp}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["time"] < self.cache_ttl:
                return entry["data"]

        try:
            # Query AMFI open API with clean search terms
            search_query = fund_name.replace("Fund", "").replace("Direct", "").replace("Growth", "").replace("Option", "").strip()
            url = f"https://api.mfapi.in/mf/search?q={search_query}"
            r = self.session.get(url, timeout=6)
            if r.status_code != 200:
                return None
            results = r.json()
            if not results:
                return None
                
            # Filter candidates having key words
            words = [w.lower() for w in fund_name.split() if w.lower() not in ['fund', 'plan', 'growth', 'scheme', 'option', '-']]
            candidates = [x for x in results if all(w in x['schemeName'].lower() for w in words)]
            if not candidates:
                candidates = results

            # Prioritize Direct Plan Growth
            direct_growth = [x for x in candidates if "direct" in x["schemeName"].lower() and "growth" in x["schemeName"].lower()]
            eval_list = direct_growth if direct_growth else candidates

            best_candidate = eval_list[0]
            best_nav = None
            best_date = None
            best_meta = {}

            # If expected_ltp provided, verify NAV is within reasonable proximity
            if expected_ltp and expected_ltp > 0:
                best_diff = 999999
                for c in eval_list[:6]:
                    sc = c["schemeCode"]
                    d_res = self.session.get(f"https://api.mfapi.in/mf/{sc}", timeout=5)
                    if d_res.status_code == 200:
                        d_data = d_res.json()
                        nav_data = d_data.get("data", [])
                        if nav_data:
                            nav_val = float(nav_data[0]["nav"])
                            diff = abs(nav_val - expected_ltp)
                            if diff < best_diff:
                                best_diff = diff
                                best_candidate = c
                                best_nav = nav_val
                                best_date = nav_data[0]["date"]
                                best_meta = d_data.get("meta", {})
            else:
                d_res = self.session.get(f"https://api.mfapi.in/mf/{best_candidate['schemeCode']}", timeout=5)
                if d_res.status_code == 200:
                    d_data = d_res.json()
                    nav_data = d_data.get("data", [])
                    if nav_data:
                        best_nav = float(nav_data[0]["nav"])
                        best_date = nav_data[0]["date"]
                        best_meta = d_data.get("meta", {})

            result = {
                "scheme_code": best_candidate["schemeCode"],
                "scheme_name": best_meta.get("scheme_name", best_candidate["schemeName"]),
                "scheme_category": best_meta.get("scheme_category", "Mutual Fund"),
                "fund_house": best_meta.get("fund_house", ""),
                "latest_nav": best_nav,
                "nav_date": best_date
            }
            self.cache[cache_key] = {"data": result, "time": time.time()}
            return result
        except Exception as e:
            logger.warning(f"Error resolving MF {fund_name}: {e}")
            return None

    def calculate_scores_and_recommendation(self, holding, tech_data, fund_data):
        current_price = holding.get("ltp", 0.0)
        if tech_data and tech_data.get("current_price"):
            current_price = tech_data["current_price"]

        # 1. Technical Score (0 to 100)
        tech_score = 50.0
        if tech_data:
            rsi = tech_data.get("rsi14", 50)
            # RSI score: Oversold (<35) is bullish buying opportunity in quality assets
            if rsi <= 20:
                tech_score += 25 # Deeply oversold
            elif rsi <= 35:
                tech_score += 15
            elif rsi >= 75:
                tech_score -= 20 # Overbought
            elif rsi >= 65:
                tech_score -= 5
                
            # Moving averages score
            sma20 = tech_data.get("sma20")
            sma50 = tech_data.get("sma50")
            sma200 = tech_data.get("sma200")
            
            if sma200:
                if current_price > sma200:
                    tech_score += 15 # Long term bull
                else:
                    tech_score -= 15
            if sma50 and current_price > sma50:
                tech_score += 10
            if sma20 and current_price > sma20:
                tech_score += 5
                
            # Support proximity: buying near support is lower risk
            support = tech_data.get("support", current_price)
            if current_price > 0 and (current_price - support) / current_price < 0.03:
                tech_score += 10
                
            tech_score = max(10, min(95, tech_score))
        
        # 2. Fundamental Score (0 to 100)
        fund_score = 50.0
        if fund_data:
            rec = str(fund_data.get("recommendation_key", "")).lower()
            if "strong_buy" in rec:
                fund_score += 25
            elif "buy" in rec:
                fund_score += 15
            elif "sell" in rec:
                fund_score -= 20
                
            num_analysts = fund_data.get("num_analysts", 0)
            if num_analysts >= 20:
                fund_score += 10 # Strong institutional coverage
                
            pe = fund_data.get("pe")
            fwd_pe = fund_data.get("forward_pe")
            if pe and fwd_pe and fwd_pe < pe:
                fund_score += 10 # Earnings growth expected
            if pe and pe < 20:
                fund_score += 10 # Value discount
            elif pe and pe > 80:
                fund_score -= 10 # Rich valuation
                
            margins = fund_data.get("profit_margins_pct")
            if margins and margins > 15:
                fund_score += 10 # High profitability
                
            fund_score = max(10, min(95, fund_score))
        elif holding.get("is_etf"):
            fund_score = 70.0 # ETFs carry lower single-stock idiosyncratic risk
        elif holding.get("is_mf"):
            fund_score = 65.0

        # Composite Score
        if fund_data and tech_data:
            composite_score = round(0.55 * fund_score + 0.45 * tech_score, 1)
        elif tech_data:
            composite_score = round(tech_score, 1)
        else:
            composite_score = 60.0

        # Consensus upside
        target_mean = None
        upside_pct = None
        if fund_data and fund_data.get("target_mean"):
            target_mean = fund_data["target_mean"]
            if current_price > 0:
                upside_pct = round(((target_mean - current_price) / current_price) * 100, 1)
                
        # Calculate Price Targets & Stop Loss
        # Target 1: Swing Resistance or +10%
        if tech_data and tech_data.get("resistance") and tech_data["resistance"] > current_price:
            t1 = tech_data["resistance"]
        else:
            t1 = round(current_price * 1.08, 2)
            
        # Target 2: Fundamental target or +20%
        if target_mean and target_mean > current_price:
            t2 = target_mean
        else:
            t2 = round(current_price * 1.20, 2)
            
        # Stop Loss: Support or -6%
        if tech_data and tech_data.get("support") and tech_data["support"] < current_price:
            sl = round(tech_data["support"] * 0.98, 2)
        else:
            sl = round(current_price * 0.94, 2)
            
        risk = max(0.01, current_price - sl)
        reward = max(0.01, t1 - current_price)
        rr_ratio = round(reward / risk, 1)

        # Recommendation determination
        if holding.get("asset_class") == "Arbitrage / Cash":
            recommendation = "HOLD / BUFFER"
            action_badge = "neutral"
            reason = "Liquid debt surrogate providing capital preservation and dry powder for market dips."
        elif composite_score >= 75 or (upside_pct and upside_pct >= 25 and composite_score >= 60):
            recommendation = "STRONG BUY"
            action_badge = "success"
            reason = f"High conviction score ({composite_score}/100) with favorable risk-reward ({rr_ratio}:1) and strong analyst upside ({upside_pct}%)."
        elif composite_score >= 60 or (tech_data and tech_data.get("rsi14", 50) < 30):
            recommendation = "ACCUMULATE"
            action_badge = "info"
            reason = f"Oversold pullback or solid fundamental backing ({composite_score}/100). Ideal accumulation zone near support ₹{sl}."
        elif composite_score <= 35:
            recommendation = "TRIM / REBALANCE"
            action_badge = "warning"
            reason = f"Weak momentum and stretched valuation. Consider trimming to reallocate to higher-conviction assets."
        else:
            recommendation = "HOLD"
            action_badge = "secondary"
            reason = "Consolidating within normal bounds. Maintain position and track trend."

        return {
            "tech_score": round(tech_score, 1) if tech_data else None,
            "fund_score": round(fund_score, 1) if fund_data else None,
            "composite_score": composite_score,
            "recommendation": recommendation,
            "action_badge": action_badge,
            "reason": reason,
            "target_1": t1,
            "target_2": t2,
            "stop_loss": sl,
            "risk_reward": rr_ratio,
            "upside_pct": upside_pct
        }

    def analyze_portfolio(self, holdings):
        """
        Enriches all holdings with live market technicals, fundamentals, AMFI data, scores, and targets.
        """
        enriched = []
        for h in holdings:
            ticker = h.get("ticker")
            tech_data = self.fetch_technical_data(ticker) if ticker else None
            fund_data = self.fetch_fundamental_data(ticker) if (ticker and h.get("is_equity")) else None
            
            # If mutual fund and no live price from ticker, try AMFI
            mf_info = None
            if h.get("is_mf") and not ticker:
                mf_info = self.fetch_mf_data(h.get("instrument", ""), h.get("ltp"))
                if mf_info and mf_info.get("latest_nav"):
                    # Use live NAV if available
                    h["live_price"] = mf_info["latest_nav"]
                    h["current_value"] = round(h["quantity"] * mf_info["latest_nav"], 2)
                    h["pnl"] = round(h["current_value"] - h["invested"], 2)
                    h["net_chg"] = round(((h["current_value"] - h["invested"]) / h["invested"] * 100), 2) if h["invested"] > 0 else 0.0
                else:
                    h["live_price"] = h.get("ltp", 0.0)
            elif tech_data and tech_data.get("current_price"):
                live_price = tech_data["current_price"]
                h["live_price"] = live_price
                h["current_value"] = round(h["quantity"] * live_price, 2)
                h["pnl"] = round(h["current_value"] - h["invested"], 2)
                h["net_chg"] = round(((h["current_value"] - h["invested"]) / h["invested"] * 100), 2) if h["invested"] > 0 else 0.0
            else:
                h["live_price"] = h.get("ltp", 0.0)

            analysis = self.calculate_scores_and_recommendation(h, tech_data, fund_data)
            
            enriched.append({
                **h,
                "technical": tech_data,
                "fundamental": fund_data,
                "mf_info": mf_info,
                "analysis": analysis
            })
            
        return enriched
