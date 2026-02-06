import { useState } from 'react';
import axios from 'axios';
import { Send, CheckCircle, AlertCircle } from 'lucide-react';

const BugReport = () => {
    const [formData, setFormData] = useState({ title: '', body: '', priority: 'medium' });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await axios.post('/api/predict', formData);
            setResult(response.data);
            setFormData({ title: '', body: '', priority: 'medium' });
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

            <div className="card">
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
