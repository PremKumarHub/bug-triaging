const StatsCard = ({ label, value, icon: Icon, color, onClick }) => {
    return (
        <div className="stats-card" onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="stats-label">{label}</span>
                {Icon && <Icon size={20} style={{ color: color }} />}
            </div>
            <span className="stats-value">{value}</span>
        </div>
    );
};

export default StatsCard;
