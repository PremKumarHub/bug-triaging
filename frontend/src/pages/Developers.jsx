import { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Mail, Shield, Activity } from 'lucide-react';

const Developers = () => {
    const [developers, setDevelopers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDevelopers = async () => {
            try {
                const response = await axios.get('/api/users?role=developer');
                setDevelopers(response.data);
            } catch (err) {
                console.error("Error fetching developers:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchDevelopers();
    }, []);

    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>Developer Management</h1>

            <div className="stats-grid">
                <div className="stats-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="stats-label">Active Developers</span>
                        <Users size={20} style={{ color: 'var(--primary)' }} />
                    </div>
                    <span className="stats-value">{developers.length}</span>
                </div>
            </div>

            <div className="card">
                <h2>Team Directory</h2>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Username</th>
                                <th>Role</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {developers.map((dev, idx) => (
                                <tr key={idx}>
                                    <td style={{ fontWeight: 600 }}>{dev.full_name}</td>
                                    <td>{dev.username}</td>
                                    <td>
                                        <span className="status-badge" style={{ background: 'var(--border)', color: 'white' }}>
                                            {dev.role}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)' }}>
                                            <Activity size={14} /> Active
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {developers.length === 0 && !loading && (
                                <tr>
                                    <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                        No developers found in the system.
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

export default Developers;
