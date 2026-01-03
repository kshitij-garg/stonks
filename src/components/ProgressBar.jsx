import { useState, useEffect, useRef } from 'react';
import { fetchProgress, fetchCacheStatus } from '../api/stockApi';
import { Loader, CheckCircle, AlertCircle, Clock, ChevronDown, ChevronUp, Database } from 'lucide-react';

function ProgressBar({ isLoading }) {
    const [progress, setProgress] = useState(null);
    const [cacheStatus, setCacheStatus] = useState({});
    const [logsExpanded, setLogsExpanded] = useState(false);
    const [visible, setVisible] = useState(false);
    const intervalRef = useRef(null);

    useEffect(() => {
        // Fetch cache status on mount
        fetchCacheStatus().then(setCacheStatus).catch(() => { });

        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        if (!isLoading) {
            if (progress?.status === 'done') {
                setTimeout(() => setVisible(false), 3000);
            }
            return;
        }

        setVisible(true);

        const pollProgress = async () => {
            try {
                const data = await fetchProgress();
                if (data) {
                    setProgress(data);
                    setCacheStatus(data.cache_status || {});
                }

                if (data?.status === 'done' || data?.status === 'error') {
                    if (intervalRef.current) {
                        clearInterval(intervalRef.current);
                        intervalRef.current = null;
                    }
                }
            } catch (e) { }
        };

        pollProgress();
        intervalRef.current = setInterval(pollProgress, 1500);

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [isLoading]);

    const percentage = progress?.total > 0
        ? Math.round((progress.current / progress.total) * 100)
        : 0;

    const getStatusIcon = () => {
        if (!progress) return <Database size={16} color="#06b6d4" />;
        switch (progress.status) {
            case 'done': return <CheckCircle size={16} color="#10b981" />;
            case 'error': return <AlertCircle size={16} color="#ef4444" />;
            case 'loading': return <Loader size={16} className="spinner" />;
            default: return <Database size={16} color="#06b6d4" />;
        }
    };

    // Always show cache status bar (minimized)
    return (
        <div className={`progress-container glass-card ${!visible && !Object.keys(cacheStatus).length ? 'hidden' : ''}`}>
            {/* Cache Status Row */}
            <div className="cache-status-row">
                <div className="cache-status-title">
                    <Database size={14} />
                    <span>Data Cache</span>
                </div>
                <div className="cache-indicators">
                    {Object.entries(cacheStatus).map(([tf, status]) => (
                        <div
                            key={tf}
                            className={`cache-indicator ${status.valid ? 'valid' : 'invalid'}`}
                            title={status.valid ? `${tf}: ${status.stocks_count} stocks, ${status.age_seconds}s old` : `${tf}: not cached`}
                        >
                            <span className="cache-dot" />
                            <span className="cache-label">{tf}</span>
                            {status.valid && <span className="cache-count">{status.stocks_count}</span>}
                        </div>
                    ))}
                </div>
            </div>

            {/* Progress Section - only show when loading */}
            {visible && progress && progress.status !== 'idle' && (
                <>
                    <div className="progress-divider" />

                    <div className="progress-header">
                        {getStatusIcon()}
                        <span className="progress-title">
                            {progress.status === 'done' ? 'Analysis Complete' :
                                progress.status === 'error' ? 'Error' :
                                    `Analyzing ${progress.active_timeframe || ''} data`}
                        </span>
                        <span className="progress-percentage">{percentage}%</span>
                    </div>

                    <div className="progress-bar-wrapper">
                        <div
                            className="progress-bar-fill"
                            style={{
                                width: `${percentage}%`,
                                background: progress.status === 'done'
                                    ? 'var(--gradient-green)'
                                    : progress.status === 'error'
                                        ? 'var(--gradient-red)'
                                        : 'var(--gradient-cyan)'
                            }}
                        />
                    </div>

                    <div className="progress-message-row">
                        <span className="progress-message">{progress.message}</span>
                        <button
                            className="logs-toggle"
                            onClick={() => setLogsExpanded(!logsExpanded)}
                        >
                            {logsExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            {logsExpanded ? 'Hide' : 'Show'} Logs
                        </button>
                    </div>

                    {logsExpanded && progress.logs?.length > 0 && (
                        <div className="progress-logs">
                            {progress.logs.slice(-10).map((log, i) => (
                                <div key={i} className="progress-log-item">
                                    <Clock size={10} />
                                    <span className="log-time">{log.time}</span>
                                    <span className="log-message">{log.message}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default ProgressBar;
