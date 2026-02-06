import { useState, useEffect } from 'react';
import axios from 'axios';
import StatsCard from '../components/StatsCard';
import { Bug, CheckCircle, AlertTriangle, Users, Clock } from 'lucide-react';

import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        total_bugs: 0,
        auto_assigned: 0,
        manual_review: 0,
        bugs_per_developer: {},
        pending_bugs: 0
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get('/api/stats');
                setStats(response.data);
            } catch (err) {
                console.error("Error fetching stats:", err);
            }
        };
        fetchStats();
    }, []);

    return (
        <div>
            <h1 style={{ marginBottom: '2rem' }}>Analytics Overview</h1>

            <div className="stats-grid">
                <StatsCard
                    label="Total Bugs"
                    value={stats.total_bugs}
                    icon={Bug}
                    color="#818cf8"
                    onClick={() => navigate('/history')}
                />
                <StatsCard
                    label="Auto Assigned"
                    value={stats.auto_assigned}
                    icon={CheckCircle}
                    color="#22c55e"
                    onClick={() => navigate('/history?status=assigned')}
                />
                <StatsCard
                    label="Manual Review"
                    value={stats.manual_review}
                    icon={AlertTriangle}
                    color="#f59e0b"
                    onClick={() => navigate('/history?status=manual-review')}
                />
                <StatsCard
                    label="Pending"
                    value={stats.pending_bugs}
                    icon={Clock}
                    color="#94a3b8"
                    onClick={() => navigate('/history?status=open')}
                />
            </div>

            <div className="card">
                <h2>Bugs per Developer</h2>
                <div className="predictions" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {Object.entries(stats.bugs_per_developer).map(([dev, count], index) => (
                        <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>{dev}</span>
                            <div style={{ flex: 1, margin: '0 1rem', height: '8px', background: '#334155', borderRadius: '4px' }}>
                                <div
                                    style={{
                                        width: `${(count / stats.total_bugs) * 100}%`,
                                        height: '100%',
                                        background: 'var(--primary)',
                                        borderRadius: '4px'
                                    }}
                                />
                            </div>
                            <span>{count}</span>
                        </div>
                    ))}
                    {Object.keys(stats.bugs_per_developer).length === 0 && (
                        <div style={{ color: 'var(--text-muted)' }}>No assignments yet.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
