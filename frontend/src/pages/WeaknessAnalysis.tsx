import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts';
import Card from '../components/common/Card';
import './WeaknessAnalysis.css';

export default function WeaknessAnalysis() {
    const [period, setPeriod] = useState('30d');

    const categoryData = [
        { name: 'Part of Speech', value: 25 },
        { name: 'Vocabulary', value: 18 },
        { name: 'Tense/Voice', value: 15 },
        { name: 'Connector', value: 12 },
    ];

    const partData = [
        { name: 'Part 5', value: 37 },
        { name: 'Part 7', value: 25 },
        { name: 'Part 6', value: 15 },
        { name: 'Part 2', value: 10 },
        { name: 'Part 3', value: 13 },
    ];

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899'];

    const trendData = Array.from({ length: 30 }, (_, i) => ({
        name: `Day ${i + 1}`,
        errors: Math.floor(Math.random() * 15) + 2
    }));

    return (
        <div className="stats-page">
            <div className="stats-header">
                <h1>Weakness Analysis</h1>
                <div className="period-tabs">
                    <button className={`tab ${period === '7d' ? 'active' : ''}`} onClick={() => setPeriod('7d')}>7 Days</button>
                    <button className={`tab ${period === '30d' ? 'active' : ''}`} onClick={() => setPeriod('30d')}>30 Days</button>
                    <button className={`tab ${period === '90d' ? 'active' : ''}`} onClick={() => setPeriod('90d')}>90 Days</button>
                    <button className={`tab ${period === 'all' ? 'active' : ''}`} onClick={() => setPeriod('all')}>All</button>
                </div>
            </div>

            <div className="charts-grid">
                <Card className="chart-card bar-chart-card">
                    <h2>Errors by Category</h2>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={categoryData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card className="chart-card pie-chart-card">
                    <h2>Errors by Part</h2>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie data={partData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" label>
                                    {partData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card className="chart-card line-chart-card">
                    <h2>Recent Study Trend</h2>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" hide />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="errors" stroke="#3b82f6" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                <Card className="summary-card">
                    <h3>Top Weakness</h3>
                    <p className="summary-text">
                        <strong>Part of Speech errors in Part 5</strong><br />
                        Focus on suffix recognition and sentence structure analysis.
                    </p>
                </Card>
            </div>
        </div>
    );
}
