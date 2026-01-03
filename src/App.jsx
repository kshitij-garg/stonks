import { useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import {
    fetchTopPerformers,
    fetchMarketOverview,
    fetchSectors,
    fetchAllStocks,
    fetchRecommendations,
    fetchBacktestResults,
    fetchWatchlist,
    addToWatchlist,
    removeFromWatchlist,
    fetchPortfolio,
    addToPortfolio,
    removeFromPortfolio,
    fetchCompareStocks
} from './api/stockApi';
import Header from './components/Header';
import MarketOverview from './components/MarketOverview';
import TopPerformers from './components/TopPerformers';
import SectorHeatmap from './components/SectorHeatmap';
import StockScreener from './components/StockScreener';
import StockDetails from './components/StockDetails';
import Recommendations from './components/Recommendations';
import Backtesting from './components/Backtesting';
import Watchlist from './components/Watchlist';
import Portfolio from './components/Portfolio';
import Compare from './components/Compare';
import ProgressBar from './components/ProgressBar';

function App() {
    const [selectedStock, setSelectedStock] = useState(null);
    const [activeTab, setActiveTab] = useState('dashboard');
    const [timeframe, setTimeframe] = useState('weekly');
    const [backtestDays, setBacktestDays] = useState(30);
    const [compareSymbols, setCompareSymbols] = useState([]);
    const queryClient = useQueryClient();

    // Market Overview
    const { data: marketData, isLoading: marketLoading, error: marketError, refetch: refetchMarket } = useQuery({
        queryKey: ['market-overview'],
        queryFn: fetchMarketOverview,
        staleTime: 1000 * 60 * 5,
        retry: 2
    });

    // Top Performers
    const { data: performersData, isLoading: performersLoading, error: performersError, isFetching: performersFetching, refetch: refetchPerformers } = useQuery({
        queryKey: ['top-performers', timeframe],
        queryFn: () => fetchTopPerformers(timeframe),
        staleTime: 1000 * 60 * 10,
        retry: 1,
        refetchOnWindowFocus: false
    });

    // Sectors
    const { data: sectorsData, isLoading: sectorsLoading, error: sectorsError, refetch: refetchSectors } = useQuery({
        queryKey: ['sectors'],
        queryFn: fetchSectors,
        staleTime: 1000 * 60 * 10,
        retry: 1
    });

    // All Stocks (for screener)
    const { data: allStocks, isLoading: allStocksLoading, isFetching: allStocksFetching, error: allStocksError, refetch: refetchAllStocks } = useQuery({
        queryKey: ['all-stocks', timeframe],
        queryFn: () => fetchAllStocks(timeframe),
        staleTime: 1000 * 60 * 10,
        retry: 1,
        enabled: activeTab === 'screener'
    });

    // Recommendations
    const { data: recommendationsData, isLoading: recommendationsLoading, isFetching: recommendationsFetching, error: recommendationsError, refetch: refetchRecommendations } = useQuery({
        queryKey: ['recommendations', timeframe],
        queryFn: () => fetchRecommendations(timeframe),
        staleTime: 1000 * 60 * 10,
        retry: 1,
        enabled: activeTab === 'recommendations'
    });

    // Backtesting
    const { data: backtestData, isLoading: backtestLoading, error: backtestError, refetch: refetchBacktest } = useQuery({
        queryKey: ['backtest', backtestDays],
        queryFn: () => fetchBacktestResults(backtestDays),
        staleTime: 1000 * 60 * 5,
        retry: 1,
        enabled: activeTab === 'backtesting'
    });

    // Watchlist
    const { data: watchlistData, isLoading: watchlistLoading, error: watchlistError, refetch: refetchWatchlist } = useQuery({
        queryKey: ['watchlist'],
        queryFn: () => fetchWatchlist(),
        staleTime: 1000 * 60 * 2,
        enabled: activeTab === 'watchlist'
    });

    const addWatchlistMutation = useMutation({
        mutationFn: (symbol) => addToWatchlist(symbol),
        onSuccess: () => refetchWatchlist()
    });

    const removeWatchlistMutation = useMutation({
        mutationFn: (symbol) => removeFromWatchlist(symbol),
        onSuccess: () => refetchWatchlist()
    });

    // Portfolio
    const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError, refetch: refetchPortfolio } = useQuery({
        queryKey: ['portfolio'],
        queryFn: fetchPortfolio,
        staleTime: 1000 * 60 * 2,
        enabled: activeTab === 'portfolio'
    });

    const addPortfolioMutation = useMutation({
        mutationFn: ({ symbol, quantity, price }) => addToPortfolio(symbol, quantity, price),
        onSuccess: () => refetchPortfolio()
    });

    const removePortfolioMutation = useMutation({
        mutationFn: (symbol) => removeFromPortfolio(symbol),
        onSuccess: () => refetchPortfolio()
    });

    // Compare
    const { data: compareData, isLoading: compareLoading, error: compareError, refetch: refetchCompare } = useQuery({
        queryKey: ['compare', compareSymbols],
        queryFn: () => fetchCompareStocks(compareSymbols),
        staleTime: 1000 * 60 * 5,
        enabled: activeTab === 'compare' && compareSymbols.length > 0
    });

    const handleStockClick = (stock) => setSelectedStock(stock);
    const handleCloseDetails = () => setSelectedStock(null);
    const handleTimeframeChange = (newTimeframe) => setTimeframe(newTimeframe);

    const handleRefreshAll = () => {
        queryClient.invalidateQueries(['top-performers']);
        queryClient.invalidateQueries(['recommendations']);
        queryClient.invalidateQueries(['all-stocks']);
        refetchPerformers();
    };

    const handleRunBacktest = (days) => {
        setBacktestDays(days);
        refetchBacktest();
    };

    const handleAddCompare = (symbol) => {
        if (!compareSymbols.includes(symbol) && compareSymbols.length < 5) {
            setCompareSymbols([...compareSymbols, symbol]);
        }
    };

    const handleRemoveCompare = (symbol) => {
        setCompareSymbols(compareSymbols.filter(s => s !== symbol));
    };

    const isDataLoading = performersFetching || allStocksFetching || recommendationsFetching;

    return (
        <div className="app">
            <Header
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                timeframe={timeframe}
                setTimeframe={handleTimeframeChange}
                onRefresh={handleRefreshAll}
            />

            <ProgressBar isLoading={isDataLoading} />

            <main className="main-content">
                {activeTab === 'dashboard' && (
                    <>
                        <MarketOverview
                            data={marketData}
                            isLoading={marketLoading}
                            error={marketError}
                            onRetry={refetchMarket}
                        />

                        {performersData && (
                            <div className="timeframe-indicator glass-card">
                                <span>📊 <strong>{timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}</strong> analysis</span>
                                <span className="timestamp">
                                    Analyzed: {performersData?.total_analyzed || 0} stocks
                                </span>
                            </div>
                        )}

                        <div className="dashboard">
                            <TopPerformers
                                data={performersData}
                                isLoading={performersLoading && !performersData}
                                error={performersError}
                                onStockClick={handleStockClick}
                                onRetry={refetchPerformers}
                                type="top"
                            />
                            <TopPerformers
                                data={performersData}
                                isLoading={performersLoading && !performersData}
                                error={performersError}
                                onStockClick={handleStockClick}
                                onRetry={refetchPerformers}
                                type="bottom"
                            />
                        </div>

                        <SectorHeatmap
                            data={sectorsData}
                            isLoading={sectorsLoading && !sectorsData}
                            error={sectorsError}
                            onRetry={refetchSectors}
                        />
                    </>
                )}

                {activeTab === 'recommendations' && (
                    <Recommendations
                        data={recommendationsData}
                        isLoading={recommendationsLoading && !recommendationsData}
                        error={recommendationsError}
                        onStockClick={handleStockClick}
                        onRetry={refetchRecommendations}
                        timeframe={timeframe}
                    />
                )}

                {activeTab === 'screener' && (
                    <StockScreener
                        stocks={allStocks}
                        isLoading={allStocksLoading && !allStocks}
                        error={allStocksError}
                        onStockClick={handleStockClick}
                        onRetry={refetchAllStocks}
                        timeframe={timeframe}
                    />
                )}

                {activeTab === 'watchlist' && (
                    <Watchlist
                        data={watchlistData}
                        isLoading={watchlistLoading}
                        error={watchlistError}
                        onStockClick={handleStockClick}
                        onRetry={refetchWatchlist}
                        onAdd={(symbol) => addWatchlistMutation.mutate(symbol)}
                        onRemove={(symbol) => removeWatchlistMutation.mutate(symbol)}
                    />
                )}

                {activeTab === 'portfolio' && (
                    <Portfolio
                        data={portfolioData}
                        isLoading={portfolioLoading}
                        error={portfolioError}
                        onStockClick={handleStockClick}
                        onRetry={refetchPortfolio}
                        onAdd={(data) => addPortfolioMutation.mutate(data)}
                        onRemove={(symbol) => removePortfolioMutation.mutate(symbol)}
                    />
                )}

                {activeTab === 'compare' && (
                    <Compare
                        data={compareData}
                        isLoading={compareLoading}
                        error={compareError}
                        onAdd={handleAddCompare}
                        onRemove={handleRemoveCompare}
                    />
                )}

                {activeTab === 'backtesting' && (
                    <Backtesting
                        data={backtestData?.data}
                        stats={backtestData?.stats}
                        isLoading={backtestLoading && !backtestData}
                        error={backtestError}
                        onRetry={refetchBacktest}
                        onRunBacktest={handleRunBacktest}
                    />
                )}
            </main>

            <div
                className={`stock-details-overlay ${selectedStock ? 'open' : ''}`}
                onClick={handleCloseDetails}
            />
            <StockDetails
                stock={selectedStock}
                onClose={handleCloseDetails}
            />
        </div>
    );
}

export default App;
