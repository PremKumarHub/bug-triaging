import { useState, useEffect } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import { Search, Filter, ExternalLink, User as UserIcon, Trash2 } from 'lucide-react';

const BugHistory = () => {
    const { search } = useLocation();
    const query = new URLSearchParams(search);
    const filterStatus = query.get('status');

    const [bugs, setBugs] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);

    // Assignment Modal State
    const [selectedBug, setSelectedBug] = useState(null);
    const [allDevelopers, setAllDevelopers] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [targetDev, setTargetDev] = useState({ id: null, name: '' });
    const [assignmentLoading, setAssignmentLoading] = useState(false);

    useEffect(() => {
        fetchBugs();
        fetchDevelopers();
    }, []);

    const fetchBugs = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/bugs');
            setBugs(response.data);
        } catch (err) {
            console.error("Error fetching bugs:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchDevelopers = async () => {
        try {
            const response = await axios.get('/api/users?role=developer');
            setAllDevelopers(response.data);
        } catch (err) {
            console.error("Error fetching developers:", err);
        }
    };

    const handleOpenAssign = async (bug) => {
        setSelectedBug(bug);
        setAssignmentLoading(true);
        try {
            const resp = await axios.get(`/api/bugs/${bug.id}/predictions`);
            setSuggestions(resp.data.predictions);
            // Default to top suggestion if it exists
            if (resp.data.predictions.length > 0) {
                const top = resp.data.predictions[0];
                const dev = allDevelopers.find(d => d.full_name === top.predicted_developer);
                setTargetDev({ id: dev?.id || null, name: top.predicted_developer });
            }
        } catch (err) {
            console.error("Error fetching predictions:", err);
            setSuggestions([]);
        } finally {
            setAssignmentLoading(false);
        }
    };

    const handleAssign = async () => {
        if (!targetDev.name) return;
        try {
            await axios.post(`/api/bugs/${selectedBug.id}/assign`, {
                developer_id: targetDev.id,
                developer_name: targetDev.name
            });
            setSelectedBug(null);
            fetchBugs(); // Refresh list
        } catch (err) {
            alert("Failed to assign: " + err.message);
        }
    };

    const handleDelete = async (bugId) => {
        if (!window.confirm(`Are you sure you want to delete bug #${bugId}?`)) return;
        try {
            await axios.delete(`/api/bugs/${bugId}`);
            fetchBugs(); // Refresh list
        } catch (err) {
            alert("Failed to delete bug: " + err.message);
        }
    };

    const filteredBugs = bugs.filter(bug => {
        const matchesSearch = bug.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            bug.id.toString().includes(searchTerm);
        const matchesStatus = filterStatus ? bug.status === filterStatus : true;
        return matchesSearch && matchesStatus;
    });

    return (
        <div>
            {/* Assignment Modal Overlay */}
            {selectedBug && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
                    <div className="card" style={{ maxWidth: '600px', width: '100%', border: '1px solid var(--primary)' }}>
                        <h2>Assign Developer to #{selectedBug.id}</h2>
                        <div style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            {selectedBug.title}
                        </div>

                        {assignmentLoading ? (
                            <div style={{ padding: '2rem', textAlign: 'center' }}>Loading suggestions...</div>
                        ) : (
                            <>
                                <div style={{ marginBottom: '1.5rem' }}>
                                    <label style={{ fontSize: '0.8rem', marginBottom: '0.5rem', display: 'block' }}>ML Suggestions</label>
                                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                        {suggestions.map((p, i) => (
                                            <button
                                                key={i}
                                                onClick={() => {
                                                    const dev = allDevelopers.find(d => d.full_name === p.predicted_developer);
                                                    setTargetDev({ id: dev?.id || null, name: p.predicted_developer });
                                                }}
                                                className="status-badge"
                                                style={{
                                                    cursor: 'pointer',
                                                    background: targetDev.name === p.developer ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                                                    border: '1px solid var(--border)',
                                                    display: 'flex',
                                                    gap: '0.5rem',
                                                    padding: '0.5rem 0.75rem',
                                                    color: 'white'
                                                }}
                                            >
                                                <span>{p.predicted_developer}</span>
                                                <span style={{ opacity: 0.7 }}>{(p.confidence * 100).toFixed(0)}%</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Choose Developer</label>
                                    <select
                                        value={targetDev.name}
                                        onChange={(e) => {
                                            const dev = allDevelopers.find(d => d.full_name === e.target.value);
                                            setTargetDev({ id: dev?.id || null, name: e.target.value });
                                        }}
                                        style={{ width: '100%', padding: '0.75rem', background: '#0f172a', color: 'white', border: '1px solid var(--border)', borderRadius: '8px' }}
                                    >
                                        <option value="">Select a developer...</option>
                                        {allDevelopers.map((dev, i) => (
                                            <option key={i} value={dev.full_name}>{dev.full_name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                                    <button className="btn" onClick={handleAssign} disabled={!targetDev.name} style={{ flex: 1 }}>Confirm Assignment</button>
                                    <button className="btn" style={{ flex: 1, background: 'transparent', border: '1px solid var(--border)' }} onClick={() => setSelectedBug(null)}>Cancel</button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1>Bug History {filterStatus && <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>(Filtered by {filterStatus})</span>}</h1>
                {filterStatus && (
                    <button className="btn" onClick={() => window.history.pushState({}, '', '/history')} style={{ background: 'transparent', border: '1px solid var(--border)', fontSize: '0.8rem' }}>
                        Clear Filter
                    </button>
                )}
            </div>

            <div className="card" style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                    <div style={{ position: 'relative', flex: 1 }}>
                        <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            placeholder="Search by ID or Title..."
                            style={{ paddingLeft: '40px' }}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Title</th>
                                <th>Status</th>
                                <th>Tags</th>
                                <th>Confidence</th>
                                <th>Assignee</th>
                                <th>Source</th>
                                <th>Created</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredBugs.map(bug => {
                                const latestAssignment = bug.assignments && bug.assignments.length > 0
                                    ? bug.assignments[bug.assignments.length - 1]
                                    : null;

                                return (
                                    <tr key={bug.id}>
                                        <td>#{bug.id}</td>
                                        <td>
                                            <div style={{ fontWeight: 600 }}>{bug.title}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {bug.body}
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`status-badge status-${bug.status}`}>
                                                {bug.status}
                                            </span>
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                                {bug.tags ? bug.tags.split(',').map((tag, idx) => (
                                                    <span key={idx} style={{
                                                        fontSize: '0.65rem',
                                                        padding: '2px 6px',
                                                        borderRadius: '4px',
                                                        background: 'rgba(255,255,255,0.1)',
                                                        border: '1px solid rgba(255,255,255,0.2)',
                                                        color: '#e2e8f0'
                                                    }}>
                                                        {tag}
                                                    </span>
                                                )) : <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>-</span>}
                                            </div>
                                        </td>
                                        <td>
                                            {bug.predictions && bug.predictions.length > 0 ? (
                                                <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                                                    {(bug.predictions[0].confidence * 100).toFixed(1)}%
                                                </span>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)' }}>-</span>
                                            )}
                                        </td>
                                        <td>
                                            {latestAssignment ? (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                    <UserIcon size={14} />
                                                    <div>
                                                        <div>{latestAssignment.developer_name}</div>
                                                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{latestAssignment.assignment_type}</div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Unassigned</span>
                                            )}
                                        </td>
                                        <td>{bug.source}</td>
                                        <td>{new Date(bug.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    onClick={() => handleOpenAssign(bug)}
                                                    style={{ background: 'transparent', border: 'none', color: 'var(--primary)', cursor: 'pointer', padding: '0.25rem' }}
                                                    title="Reassign / Assign"
                                                >
                                                    <ExternalLink size={18} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(bug.id)}
                                                    style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: '0.25rem' }}
                                                    title="Delete Bug"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                            {filteredBugs.length === 0 && !loading && (
                                <tr>
                                    <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                        No bugs found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default BugHistory;
