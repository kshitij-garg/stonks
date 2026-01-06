import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, TrendingUp, Building2 } from 'lucide-react';

function SearchBar({ onSelectStock }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const inputRef = useRef(null);
    const dropdownRef = useRef(null);

    // Debounced search
    const searchStocks = useCallback(async (searchQuery) => {
        if (!searchQuery || searchQuery.length < 1) {
            setResults([]);
            setIsOpen(false);
            return;
        }

        setIsLoading(true);
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&limit=8`);
            const data = await response.json();

            if (data.success) {
                setResults(data.data);
                setIsOpen(data.data.length > 0);
                setSelectedIndex(-1);
            }
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Debounce effect
    useEffect(() => {
        const timer = setTimeout(() => {
            searchStocks(query);
        }, 150);

        return () => clearTimeout(timer);
    }, [query, searchStocks]);

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target) &&
                inputRef.current && !inputRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (stock) => {
        setQuery('');
        setIsOpen(false);
        setResults([]);
        onSelectStock?.(stock.symbol);
    };

    const handleKeyDown = (e) => {
        if (!isOpen || results.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
                break;
            case 'ArrowUp':
                e.preventDefault();
                setSelectedIndex(prev => Math.max(prev - 1, -1));
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && results[selectedIndex]) {
                    handleSelect(results[selectedIndex]);
                }
                break;
            case 'Escape':
                setIsOpen(false);
                inputRef.current?.blur();
                break;
            default:
                break;
        }
    };

    const clearSearch = () => {
        setQuery('');
        setResults([]);
        setIsOpen(false);
        inputRef.current?.focus();
    };

    return (
        <div className="search-bar-container">
            <div className="search-input-wrapper">
                <Search size={16} className="search-icon" />
                <input
                    ref={inputRef}
                    type="text"
                    className="search-input"
                    placeholder="Search stocks..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => results.length > 0 && setIsOpen(true)}
                />
                {query && (
                    <button className="search-clear" onClick={clearSearch}>
                        <X size={14} />
                    </button>
                )}
                {isLoading && <div className="search-spinner" />}
            </div>

            {isOpen && results.length > 0 && (
                <div className="search-dropdown glass-card" ref={dropdownRef}>
                    {results.map((stock, index) => (
                        <div
                            key={stock.symbol}
                            className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
                            onClick={() => handleSelect(stock)}
                            onMouseEnter={() => setSelectedIndex(index)}
                        >
                            <div className="result-main">
                                <span className="result-symbol">{stock.symbol}</span>
                                <span className="result-name">{stock.name}</span>
                            </div>
                            <div className="result-meta">
                                <span className="result-sector">
                                    <Building2 size={10} />
                                    {stock.sector}
                                </span>
                                <span className={`result-cap ${stock.cap.toLowerCase()}`}>
                                    {stock.cap}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default SearchBar;
