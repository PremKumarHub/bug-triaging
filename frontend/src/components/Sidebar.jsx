import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Bug, History, Settings, FileText, Users } from 'lucide-react';

const Sidebar = () => {
    return (
        <div className="sidebar">
            <div className="logo">BugTriage AI</div>
            <nav className="nav-links">
                <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <LayoutDashboard size={20} />
                    <span>Dashboard</span>
                </NavLink>
                <NavLink to="/report" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <FileText size={20} />
                    <span>Report Bug</span>
                </NavLink>
                <NavLink to="/history" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <History size={20} />
                    <span>Bug History</span>
                </NavLink>
                <NavLink to="/developers" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                    <Users size={20} />
                    <span>Developers</span>
                </NavLink>
            </nav>
        </div>
    );
};

export default Sidebar;
