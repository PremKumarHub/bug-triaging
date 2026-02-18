import { useState } from 'react';
import axios from 'axios';
import { Send, CheckCircle, AlertCircle } from 'lucide-react';

const BugReport = () => {
    const [formData, setFormData] = useState({ title: '', body: '', priority: 'medium', source: 'manual' });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [githubCount, setGithubCount] = useState(5);
    const [githubLoading, setGithubLoading] = useState(false);
    const [githubResult, setGithubResult] = useState(null);
    const [localCount, setLocalCount] = useState(5);
    const [localLoading, setLocalLoading] = useState(false);

    const handleGithubFetch = async () => {
        setGithubLoading(true);
        setError(null);
        setGithubResult(null);

        try {
            const response = await axios.post('/api/fetch-github', { count: githubCount });
            setGithubResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Failed to fetch from GitHub');
        } finally {
            setGithubLoading(false);
        }
    };

    const handleLocalImport = async () => {
        setLocalLoading(true);
        setError(null);
        setGithubResult(null);

        try {
            const response = await axios.post('/api/import-local', { count: localCount });
            setGithubResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Failed to import from local file');
        } finally {
            setLocalLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);
        setGithubResult(null);

        try {
            const response = await axios.post('/api/predict', formData);
            setResult(response.data);
            setFormData({ title: '', body: '', priority: 'medium', source: 'manual' });
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                setError(detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', '));
            } else {
                setError(detail || err.message || 'An error occurred');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '800px' }}>
            <h1 style={{ marginBottom: '2rem' }}>Report a New Bug</h1>

            <div className="card" style={{ marginBottom: '2rem', border: '1px border var(--primary-light)' }}>
                <h3 style={{ marginTop: 0, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={20} className="text-primary" />
                    Data Import Tools
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                    Fetch real bug reports from official VS Code repositories. Existing issues will be automatically skipped.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <div style={{ borderRight: '1px solid var(--border)', paddingRight: '1rem' }}>
                        <h4 style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>GitHub Fetch</h4>
                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                                <label style={{ fontSize: '0.75rem' }}>Count</label>
                                <input
                                    type="number"
                                    min="1"
                                    max="50"
                                    value={githubCount}
                                    onChange={(e) => setGithubCount(parseInt(e.target.value))}
                                />
                            </div>
                            <button
                                onClick={handleGithubFetch}
                                className="btn"
                                disabled={githubLoading || localLoading}
                                style={{ height: '42px', whiteSpace: 'nowrap', padding: '0 1rem', fontSize: '0.875rem' }}
                            >
                                {githubLoading ? 'Fetching...' : 'GitHub'}
                            </button>
                        </div>
                    </div>

                    <div>
                        <h4 style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>Local Import</h4>
                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                                <label style={{ fontSize: '0.75rem' }}>Count</label>
                                <input
                                    type="number"
                                    min="1"
                                    max="100"
                                    value={localCount}
                                    onChange={(e) => setLocalCount(parseInt(e.target.value))}
                                />
                            </div>
                            <button
                                onClick={handleLocalImport}
                                className="btn btn-secondary"
                                disabled={githubLoading || localLoading}
                                style={{ height: '42px', whiteSpace: 'nowrap', padding: '0 1rem', fontSize: '0.875rem' }}
                            >
                                {localLoading ? 'Importing...' : 'Local File'}
                            </button>
                        </div>
                    </div>
                </div>

                {githubResult && (
                    <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#0f172a', borderRadius: '0.5rem', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', textAlign: 'center' }}>
                            <div>
                                <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)' }}>{githubResult.imported_count}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Imported</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--warning)' }}>{githubResult.skipped_count}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Skipped</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--danger)' }}>{githubResult.error_count}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Errors</div>
                            </div>
                        </div>

                        {githubResult.imported_count > 0 && (
                            <div style={{ marginTop: '1rem', borderTop: '1px solid #334155', paddingTop: '1rem' }}>
                                <div style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Recently Imported:</div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                    {githubResult.imported.slice(0, 3).map((bug, idx) => (
                                        <div key={idx} style={{ fontSize: '0.75rem', display: 'flex', justifyContent: 'space-between', background: '#1e293b', padding: '0.5rem', borderRadius: '0.25rem' }}>
                                            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '1rem' }}>{bug.title}</span>
                                            <span style={{ color: 'var(--success)', flexShrink: 0 }}>ID: {bug.bug_id}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="card">
                <h3 style={{ marginTop: 0, marginBottom: '1.5rem' }}>Manual Entry</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Bug Title</label>
                        <input
                            type="text"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            placeholder="Brief summary of the issue..."
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Priority</label>
                        <select
                            value={formData.priority}
                            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                        >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Bug Description</label>
                        <textarea
                            value={formData.body}
                            onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                            placeholder="Detail steps to reproduce, expected vs actual behavior..."
                            rows={6}
                            required
                        />
                    </div>

                    <button type="submit" className="btn" disabled={loading} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        {loading ? 'Analyzing...' : <><Send size={18} /> Submit Bug</>}
                    </button>
                </form>

                {error && (
                    <div style={{ marginTop: '1.5rem', color: 'var(--danger)', display: 'flex', gap: '0.5rem' }}>
                        <AlertCircle size={20} /> {error}
                    </div>
                )}

                {result && (
                    <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#0f172a', borderRadius: '0.5rem', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h3 style={{ margin: 0 }}>Triage Result</h3>
                            <span className={`status-badge ${result.is_auto_assigned ? 'status-assigned' : 'status-review'}`}>
                                {result.is_auto_assigned ? 'Auto-Assigned' : 'Manual Review Required'}
                            </span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {result.predictions.map((pred, idx) => (
                                <div key={idx}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                        <span style={{ fontSize: '0.875rem' }}>{pred.predicted_developer}</span>
                                        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{(pred.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                    <div style={{ height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
                                        <div
                                            style={{
                                                width: `${pred.confidence * 100}%`,
                                                height: '100%',
                                                background: pred.confidence >= result.threshold ? 'var(--success)' : 'var(--primary)'
                                            }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>

                        {result.is_auto_assigned && (
                            <div style={{ marginTop: '1.5rem', color: 'var(--success)', display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.875rem' }}>
                                <CheckCircle size={16} />
                                Bug has been automatically assigned to <strong>{result.predictions[0].predicted_developer}</strong>.
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default BugReport;
