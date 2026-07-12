import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { BookX, TrendingUp, Calendar, AlertTriangle } from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
    return (
        <div className="dashboard">
            <h1>Dashboard</h1>

            <div className="stats-grid">
                <Card className="stat-card">
                    <div className="stat-icon-wrapper blue"><BookX size={24} /></div>
                    <div className="stat-info">
                        <span className="stat-label">Total Wrong Notes</span>
                        <span className="stat-value">127</span>
                    </div>
                </Card>
                <Card className="stat-card">
                    <div className="stat-icon-wrapper orange"><AlertTriangle size={24} /></div>
                    <div className="stat-info">
                        <span className="stat-label">Most Common Error</span>
                        <span className="stat-value text-md">Part of Speech</span>
                    </div>
                </Card>
                <Card className="stat-card">
                    <div className="stat-icon-wrapper green"><Calendar size={24} /></div>
                    <div className="stat-info">
                        <span className="stat-label">This Week</span>
                        <span className="stat-value">12 analyzed</span>
                    </div>
                </Card>
                <Card className="stat-card">
                    <div className="stat-icon-wrapper purple"><TrendingUp size={24} /></div>
                    <div className="stat-info">
                        <span className="stat-label">Accuracy Trend</span>
                        <span className="stat-value text-green">↑ 15%</span>
                    </div>
                </Card>
            </div>

            <div className="action-section">
                <Link to="/analyze">
                    <Button size="lg" fullWidth>Start New Analysis</Button>
                </Link>
            </div>

            <h2 className="section-title">Recent Analysis</h2>
            <Card className="recent-table-card">
                <table className="recent-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Part</th>
                            <th>Error Type</th>
                            <th>Question Preview</th>
                        </tr>
                    </thead>
                    <tbody>
                        {[1, 2, 3, 4, 5].map((item) => (
                            <tr key={item}>
                                <td>2026-07-12</td>
                                <td><span className="badge badge-blue">Part 5</span></td>
                                <td><span className="badge badge-orange">Part of Speech</span></td>
                                <td className="text-truncate">The company's ------- to the new market was successful.</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </Card>
        </div>
    );
}
