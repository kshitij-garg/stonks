import { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * Error Boundary component for catching React errors
 */
class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ errorInfo });
        console.error('Panel Error:', error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
        this.props.onRetry?.();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-panel glass-card">
                    <div className="error-content">
                        <AlertTriangle size={32} color="#ef4444" />
                        <h3>{this.props.panelName || 'Panel'} Error</h3>
                        <p className="error-message">
                            {this.state.error?.message || 'Something went wrong'}
                        </p>
                        {this.props.showDetails && this.state.errorInfo && (
                            <details className="error-details">
                                <summary>Technical Details</summary>
                                <pre>{this.state.errorInfo.componentStack}</pre>
                            </details>
                        )}
                        <button className="retry-btn" onClick={this.handleRetry}>
                            <RefreshCw size={14} />
                            Retry
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

/**
 * Panel wrapper with error handling and loading states
 */
function Panel({
    title,
    icon: Icon,
    iconColor = '#06b6d4',
    children,
    isLoading,
    error,
    onRetry,
    actions,
    className = ''
}) {
    if (error) {
        return (
            <div className={`section glass-card ${className}`}>
                <div className="section-header">
                    {Icon && <Icon size={20} color={iconColor} />}
                    <h3 className="section-title">{title}</h3>
                </div>
                <div className="panel-error">
                    <AlertTriangle size={24} color="#ef4444" />
                    <p>{typeof error === 'string' ? error : error?.message || 'Failed to load data'}</p>
                    {onRetry && (
                        <button className="retry-btn" onClick={onRetry}>
                            <RefreshCw size={14} />
                            Retry
                        </button>
                    )}
                </div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className={`section glass-card ${className}`}>
                <div className="section-header">
                    {Icon && <Icon size={20} color={iconColor} />}
                    <h3 className="section-title">{title}</h3>
                </div>
                <div className="loading">
                    <div className="loading-spinner" />
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <ErrorBoundary panelName={title} onRetry={onRetry}>
            <div className={`section glass-card ${className}`}>
                <div className="section-header">
                    {Icon && <Icon size={20} color={iconColor} />}
                    <h3 className="section-title">{title}</h3>
                    {actions && <div className="section-actions">{actions}</div>}
                </div>
                {children}
            </div>
        </ErrorBoundary>
    );
}

export { ErrorBoundary, Panel };
export default Panel;
