import os
from csv_parser import parse_holdings_csv
from analyzer import MarketAnalyzer
from rebalancer import PortfolioRebalancer, STRATEGIES

def test_pipeline():
    sample_file = os.path.join(os.path.dirname(__file__), "data", "sample_holdings.csv")
    with open(sample_file, "r", encoding="utf-8") as f:
        csv_text = f.read()

    holdings = parse_holdings_csv(csv_text)
    print(f"[OK] Parsed {len(holdings)} holdings from CSV.")
    assert len(holdings) == 22, f"Expected 22 holdings, got {len(holdings)}"

    analyzer = MarketAnalyzer()
    enriched = analyzer.analyze_portfolio(holdings)
    print(f"[OK] Enriched {len(enriched)} holdings with live technicals and fundamentals.")

    rebalancer = PortfolioRebalancer()
    metrics = rebalancer.compute_portfolio_metrics(enriched)
    print(f"[OK] Total Portfolio Value: Rs. {metrics['total_current_value']:,.2f}")
    print(f"[OK] Total P&L: Rs. {metrics['total_pnl']:,.2f} ({metrics['total_pnl_pct']}%)")
    print(f"[OK] Asset Classes found: {list(metrics['class_breakdown'].keys())}")

    # Test rebalancing plan
    plan = rebalancer.generate_rebalance_plan(
        enriched,
        strategy_key="core_satellite",
        rebalance_mode="smart_inflow",
        fresh_capital=100000.0,
        tolerance_band=3.0
    )
    print(f"[OK] Generated Rebalance Plan for strategy '{plan['strategy_name']}'")
    print(f"[OK] Orders count: {len(plan['orders'])}, Basket orders: {len(plan['basket_orders'])}")
    print(f"[OK] Total Buy Value: Rs. {plan['summary']['total_buy_value']:,.2f}")
    print(f"[OK] Deploy Cash Surplus: Rs. {plan['summary']['deploy_cash_value']:,.2f}")
    print("\n--- ALL BACKEND INTEGRATION TESTS PASSED ---")

if __name__ == "__main__":
    test_pipeline()
