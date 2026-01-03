import { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, Search, Filter, X } from 'lucide-react';

/**
 * Reusable DataTable component with sorting and filtering
 */
function DataTable({
    data = [],
    columns = [],
    onRowClick,
    emptyMessage = "No data available",
    pageSize = 20
}) {
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'desc' });
    const [filters, setFilters] = useState({});
    const [searchTerm, setSearchTerm] = useState('');
    const [showFilters, setShowFilters] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);

    // Get unique values for filter dropdowns
    const filterOptions = useMemo(() => {
        const options = {};
        columns.filter(c => c.filterable).forEach(col => {
            const uniqueValues = [...new Set(data.map(row => {
                const value = col.accessor(row);
                return value?.toString() || '';
            }))].filter(Boolean).sort();
            options[col.key] = uniqueValues;
        });
        return options;
    }, [data, columns]);

    // Sort and filter data
    const processedData = useMemo(() => {
        let result = [...data];

        // Apply search
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            result = result.filter(row =>
                columns.some(col => {
                    const value = col.accessor(row);
                    return value?.toString().toLowerCase().includes(term);
                })
            );
        }

        // Apply filters
        Object.entries(filters).forEach(([key, value]) => {
            if (value) {
                const column = columns.find(c => c.key === key);
                if (column) {
                    result = result.filter(row => {
                        const cellValue = column.accessor(row);
                        return cellValue?.toString() === value;
                    });
                }
            }
        });

        // Apply sorting
        if (sortConfig.key) {
            const column = columns.find(c => c.key === sortConfig.key);
            if (column) {
                result.sort((a, b) => {
                    const aVal = column.accessor(a);
                    const bVal = column.accessor(b);

                    // Handle numeric sorting
                    if (typeof aVal === 'number' && typeof bVal === 'number') {
                        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
                    }

                    // Handle string sorting
                    const aStr = String(aVal || '');
                    const bStr = String(bVal || '');
                    return sortConfig.direction === 'asc'
                        ? aStr.localeCompare(bStr)
                        : bStr.localeCompare(aStr);
                });
            }
        }

        return result;
    }, [data, searchTerm, filters, sortConfig, columns]);

    // Pagination
    const totalPages = Math.ceil(processedData.length / pageSize);
    const paginatedData = processedData.slice(
        (currentPage - 1) * pageSize,
        currentPage * pageSize
    );

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
        }));
    };

    const clearFilters = () => {
        setFilters({});
        setSearchTerm('');
    };

    const hasActiveFilters = searchTerm || Object.values(filters).some(Boolean);

    if (!data.length) {
        return (
            <div className="data-table-empty">
                <p>{emptyMessage}</p>
            </div>
        );
    }

    return (
        <div className="data-table-container">
            {/* Toolbar */}
            <div className="data-table-toolbar">
                <div className="search-box">
                    <Search size={14} />
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                    />
                    {searchTerm && (
                        <button onClick={() => setSearchTerm('')} className="clear-btn">
                            <X size={12} />
                        </button>
                    )}
                </div>

                <button
                    className={`filter-toggle ${showFilters ? 'active' : ''}`}
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <Filter size={14} />
                    Filters
                    {hasActiveFilters && <span className="filter-badge">●</span>}
                </button>

                {hasActiveFilters && (
                    <button className="clear-all-btn" onClick={clearFilters}>
                        Clear All
                    </button>
                )}

                <span className="results-count">
                    {processedData.length} of {data.length} rows
                </span>
            </div>

            {/* Filter Dropdowns */}
            {showFilters && (
                <div className="filter-row">
                    {columns.filter(c => c.filterable).map(col => (
                        <div key={col.key} className="filter-select">
                            <label>{col.label}</label>
                            <select
                                value={filters[col.key] || ''}
                                onChange={(e) => {
                                    setFilters(prev => ({ ...prev, [col.key]: e.target.value }));
                                    setCurrentPage(1);
                                }}
                            >
                                <option value="">All</option>
                                {filterOptions[col.key]?.map(opt => (
                                    <option key={opt} value={opt}>{opt}</option>
                                ))}
                            </select>
                        </div>
                    ))}
                </div>
            )}

            {/* Table */}
            <div className="data-table-wrapper">
                <table className="data-table">
                    <thead>
                        <tr>
                            {columns.map(col => (
                                <th
                                    key={col.key}
                                    onClick={() => col.sortable !== false && handleSort(col.key)}
                                    className={col.sortable !== false ? 'sortable' : ''}
                                    style={{ width: col.width }}
                                >
                                    <div className="th-content">
                                        {col.label}
                                        {sortConfig.key === col.key && (
                                            sortConfig.direction === 'asc'
                                                ? <ChevronUp size={14} />
                                                : <ChevronDown size={14} />
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {paginatedData.map((row, i) => (
                            <tr
                                key={row.symbol || i}
                                onClick={() => onRowClick?.(row)}
                                className={onRowClick ? 'clickable' : ''}
                            >
                                {columns.map(col => (
                                    <td key={col.key} className={col.className}>
                                        {col.render ? col.render(row) : col.accessor(row)}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="pagination">
                    <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </button>
                    <span>Page {currentPage} of {totalPages}</span>
                    <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}

export default DataTable;
