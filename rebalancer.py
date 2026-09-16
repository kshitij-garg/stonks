import math

STRATEGIES = {
    "core_satellite": {
        "name": "Strategic Core-Satellite (Recommended)",
        "description": "40% Core Equity & Index ETFs, 25% Mid/Small Satellite Alpha, 10% Gold & Silver Hedge, 25% Cash/Arbitrage Tactical Buffer.",
        "targets": {
            "Direct Equities": 18.0,
            "Index & Sectoral ETFs": 22.0,
            "Mutual Funds": 25.0,
            "Commodities": 10.0,
            "Arbitrage / Cash": 25.0
        }
    },
    "balanced_growth": {
        "name": "Aggressive Growth",
        "description": "High equity tilt with reduced cash buffer: 25% Direct Equity, 30% Index ETFs, 25% Mutual Funds, 10% Commodities, 10% Arbitrage Buffer.",
        "targets": {
            "Direct Equities": 25.0,
            "Index & Sectoral ETFs": 30.0,
            "Mutual Funds": 25.0,
            "Commodities": 10.0,
            "Arbitrage / Cash": 10.0
        }
    },
    "wealth_preservation": {
        "name": "Conservative Wealth Preservation",
        "description": "Defensive posture: 40% Arbitrage Cash Buffer, 15% Gold & Silver Hedge, 15% Bluechip Equities, 15% Index ETFs, 15% Mutual Funds.",
        "targets": {
            "Direct Equities": 15.0,
            "Index & Sectoral ETFs": 15.0,
            "Mutual Funds": 15.0,
            "Commodities": 15.0,
            "Arbitrage / Cash": 40.0
        }
    },
    "risk_parity": {
        "name": "All-Weather Risk Parity",
        "description": "Balanced risk distribution: 35% Equities/ETFs, 20% Commodities (Gold/Silver), 15% Mutual Funds, 30% Arbitrage/Debt reserve.",
        "targets": {
            "Direct Equities": 15.0,
            "Index & Sectoral ETFs": 20.0,
            "Mutual Funds": 15.0,
            "Commodities": 20.0,
            "Arbitrage / Cash": 30.0
        }
    }
}

class PortfolioRebalancer:
    def __init__(self):
        pass

    def compute_portfolio_metrics(self, enriched_holdings):
        total_invested = sum(h.get("invested", 0.0) for h in enriched_holdings)
        total_current_val = sum(h.get("current_value", 0.0) for h in enriched_holdings)
        total_pnl = total_current_val - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
        
        # Calculate daily change estimate
        day_pnl = sum((h.get("current_value", 0.0) * (h.get("day_chg", 0.0) / 100.0)) for h in enriched_holdings)
        day_pnl_pct = (day_pnl / total_current_val * 100) if total_current_val > 0 else 0.0
        
        # Breakdown by asset class
        class_breakdown = {}
        for h in enriched_holdings:
            ac = h.get("asset_class", "Other")
            val = h.get("current_value", 0.0)
            if ac not in class_breakdown:
                class_breakdown[ac] = {"value": 0.0, "invested": 0.0, "holdings_count": 0}
            class_breakdown[ac]["value"] += val
            class_breakdown[ac]["invested"] += h.get("invested", 0.0)
            class_breakdown[ac]["holdings_count"] += 1
            
        for ac, data in class_breakdown.items():
            data["weight_pct"] = round((data["value"] / total_current_val * 100.0), 2) if total_current_val > 0 else 0.0
            data["pnl"] = round(data["value"] - data["invested"], 2)
            data["pnl_pct"] = round((data["pnl"] / data["invested"] * 100.0), 2) if data["invested"] > 0 else 0.0
            data["value"] = round(data["value"], 2)

        return {
            "total_invested": round(total_invested, 2),
            "total_current_value": round(total_current_val, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "day_pnl": round(day_pnl, 2),
            "day_pnl_pct": round(day_pnl_pct, 2),
            "class_breakdown": class_breakdown,
            "total_holdings": len(enriched_holdings)
        }

    def generate_rebalance_plan(self, enriched_holdings, strategy_key="core_satellite", 
                                rebalance_mode="smart_inflow", fresh_capital=0.0, 
                                tolerance_band=3.0, custom_targets=None):
        """
        Generates comprehensive rebalance plan with target weights, drift analysis,
        and actionable trade orders.
        """
        metrics = self.compute_portfolio_metrics(enriched_holdings)
        total_current_val = metrics["total_current_value"]
        total_rebalance_pool = total_current_val + fresh_capital
        
        strategy = STRATEGIES.get(strategy_key, STRATEGIES["core_satellite"])
        target_weights = custom_targets if custom_targets else strategy["targets"].copy()

        # Ensure all asset classes are represented
        for ac in metrics["class_breakdown"]:
            if ac not in target_weights:
                target_weights[ac] = 0.0
                
        # 1. Asset Class Level Drift Analysis
        class_drift = {}
        for ac, data in metrics["class_breakdown"].items():
            curr_weight = data["weight_pct"]
            target_weight = target_weights.get(ac, 0.0)
            target_val = round(total_rebalance_pool * (target_weight / 100.0), 2)
            drift_pct = round(curr_weight - target_weight, 2)
            drift_val = round(data["value"] - target_val, 2)
            
            # Status based on tolerance band
            if abs(drift_pct) <= tolerance_band:
                status = "Within Tolerance"
                action = "HOLD"
            elif drift_pct > tolerance_band:
                status = "Overweight"
                action = "TRIM / HARVEST" if rebalance_mode == "full_rebalance" else "HOLD (OVERWEIGHT)"
            else:
                status = "Underweight"
                action = "BUY / ALLOCATE"

            class_drift[ac] = {
                "current_value": data["value"],
                "current_weight_pct": curr_weight,
                "target_weight_pct": target_weight,
                "target_value": target_val,
                "drift_pct": drift_pct,
                "drift_value": drift_val,
                "status": status,
                "action": action
            }

        # 2. Holding-Level Target Allocation & Orders
        orders = []
        
        # Group holdings by asset class
        grouped = {}
        for h in enriched_holdings:
            ac = h.get("asset_class", "Other")
            if ac not in grouped:
                grouped[ac] = []
            grouped[ac].append(h)

        # Distribute class target values to individual holdings
        for ac, holdings in grouped.items():
            class_target_val = round(total_rebalance_pool * (target_weights.get(ac, 0.0) / 100.0), 2)
            curr_class_val = metrics["class_breakdown"].get(ac, {}).get("value", 0.0)
            
            # Intra-class weighting: Tilt weights towards high composite scores and oversold RSI
            score_weights = []
            for h in holdings:
                analysis = h.get("analysis") or {}
                comp_score = analysis.get("composite_score", 50.0)
                # Boost weight for oversold quality
                tech = h.get("technical") or {}
                if tech.get("rsi14", 50) < 30:
                    comp_score *= 1.25
                score_weights.append(comp_score)
                
            total_score = sum(score_weights) if sum(score_weights) > 0 else len(holdings)
            normalized_intra_weights = [s / total_score for s in score_weights]

            for i, h in enumerate(holdings):
                holding_target_val = round(class_target_val * normalized_intra_weights[i], 2)
                curr_val = h.get("current_value", 0.0)
                diff_val = holding_target_val - curr_val
                diff_pct_of_portfolio = (diff_val / total_rebalance_pool * 100) if total_rebalance_pool > 0 else 0
                
                price = h.get("live_price", h.get("ltp", 1.0))
                if price <= 0:
                    price = 1.0

                action = "HOLD"
                order_qty = 0
                order_amount = 0.0
                priority = "MEDIUM"
                
                analysis = h.get("analysis") or {}
                tech = h.get("technical") or {}

                # Determine action based on rebalance mode & drift
                if ac == "Arbitrage / Cash":
                    if diff_val < 0:
                        # Arbitrage fund has surplus cash to deploy
                        action = "DEPLOY CASH"
                        order_amount = abs(diff_val)
                        order_qty = round(order_amount / price, 3)
                        priority = "HIGH"
                    else:
                        action = "HOLD BUFFER"
                        order_amount = 0.0
                elif diff_val > 0 and abs(diff_pct_of_portfolio) >= (tolerance_band / 2):
                    action = "BUY"
                    order_amount = diff_val
                    # Round down to whole shares for equities and ETFs, decimal for MFs
                    order_qty = math.floor(order_amount / price) if (h.get("is_equity") or h.get("is_etf")) else round(order_amount / price, 3)
                    order_amount = round(order_qty * price, 2)
                    comp_score = analysis.get("composite_score", 50)
                    priority = "HIGH" if comp_score >= 70 or tech.get("rsi14", 50) < 30 else "MEDIUM"
                elif diff_val < 0 and abs(diff_pct_of_portfolio) >= tolerance_band and rebalance_mode == "full_rebalance":
                    action = "SELL"
                    order_amount = abs(diff_val)
                    order_qty = math.floor(order_amount / price) if (h.get("is_equity") or h.get("is_etf")) else round(order_amount / price, 3)
                    order_amount = round(order_qty * price, 2)
                    priority = "LOW"
                else:
                    action = "HOLD"

                orders.append({
                    "instrument": h.get("instrument"),
                    "asset_class": h.get("asset_class"),
                    "current_quantity": h.get("quantity"),
                    "current_value": curr_val,
                    "current_weight_pct": round((curr_val / total_current_val * 100), 2) if total_current_val > 0 else 0,
                    "target_value": holding_target_val,
                    "target_weight_pct": round((holding_target_val / total_rebalance_pool * 100), 2) if total_rebalance_pool > 0 else 0,
                    "price": price,
                    "action": action,
                    "order_quantity": order_qty,
                    "order_amount": order_amount,
                    "priority": priority,
                    "composite_score": analysis.get("composite_score", 50),
                    "recommendation": analysis.get("recommendation", "HOLD"),
                    "target_1": analysis.get("target_1"),
                    "target_2": analysis.get("target_2"),
                    "stop_loss": analysis.get("stop_loss"),
                    "rsi14": tech.get("rsi14") if tech else None
                })

        # Sort orders: Action BUYs first by priority, then DEPLOY CASH, then SELLs, then HOLDs
        priority_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        action_rank = {"BUY": 4, "DEPLOY CASH": 3, "SELL": 2, "HOLD BUFFER": 1, "HOLD": 0}
        
        orders.sort(key=lambda x: (
            action_rank.get(x["action"], 0),
            priority_rank.get(x["priority"], 0),
            x.get("order_amount", 0)
        ), reverse=True)

        # Summary statistics
        total_buy_val = sum(o["order_amount"] for o in orders if o["action"] == "BUY")
        total_sell_val = sum(o["order_amount"] for o in orders if o["action"] == "SELL")
        deploy_cash_val = sum(o["order_amount"] for o in orders if o["action"] == "DEPLOY CASH")
        
        # Build Zerodha Kite basket orders
        basket_orders = []
        for o in orders:
            if o["action"] in ["BUY", "SELL"] and o["order_quantity"] > 0:
                symbol = o["instrument"]
                # Clean instrument name for broker ticker
                clean_sym = symbol.split()[0].replace(".NS", "")
                basket_orders.append({
                    "variety": "regular",
                    "tradingsymbol": clean_sym,
                    "exchange": "NSE",
                    "transaction_type": o["action"],
                    "order_type": "LIMIT",
                    "quantity": int(o["order_quantity"]) if o["order_quantity"] >= 1 else 1,
                    "price": round(o["price"], 2),
                    "product": "CNC",
                    "tag": "QuantRebalance"
                })

        return {
            "strategy_key": strategy_key,
            "strategy_name": strategy["name"],
            "rebalance_mode": rebalance_mode,
            "tolerance_band": tolerance_band,
            "fresh_capital": fresh_capital,
            "total_rebalance_pool": round(total_rebalance_pool, 2),
            "class_drift": class_drift,
            "orders": orders,
            "basket_orders": basket_orders,
            "summary": {
                "total_buy_value": round(total_buy_val, 2),
                "total_sell_value": round(total_sell_val, 2),
                "deploy_cash_value": round(deploy_cash_val, 2),
                "net_capital_required": round(total_buy_val - total_sell_val, 2),
                "num_buys": len([o for o in orders if o["action"] == "BUY"]),
                "num_sells": len([o for o in orders if o["action"] == "SELL"]),
                "num_holds": len([o for o in orders if "HOLD" in o["action"]])
            }
        }
