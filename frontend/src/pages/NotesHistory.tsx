import { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { Search } from 'lucide-react';
import './NotesHistory.css';

export default function NotesHistory() {
    const [searchTerm, setSearchTerm] = useState('');

    return (
        <div className="notes-page">
            <h1>Wrong Note History</h1>

            <div className="filters-section">
                <input type="date" className="form-control filter-input" />
                <select className="form-control filter-input">
                    <option value="">All Parts</option>
                    <option value="5">Part 5</option>
                    <option value="6">Part 6</option>
                    <option value="7">Part 7</option>
                </select>
                <select className="form-control filter-input">
                    <option value="">All Categories</option>
                    <option value="part_of_speech">Part of Speech</option>
                    <option value="vocabulary">Vocabulary</option>
                </select>
                <div className="search-box">
                    <Search className="search-icon" size={18} />
                    <input
                        type="text"
                        className="form-control filter-input search-input"
                        placeholder="Search..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="notes-list">
                {[1, 2, 3, 4, 5, 6].map(item => (
                    <Card key={item} className="note-item-card">
                        <div className="note-meta">
                            <span className="note-date">2026-07-12</span>
                            <span className="badge badge-blue">Part 5</span>
                            <span className="badge badge-orange">Part of Speech</span>
                        </div>
                        <div className="note-content">
                            The company's ------- to the new market was successful.
                        </div>
                        <div className="note-actions">
                            <Button variant="outline" size="sm">View</Button>
                            <Button variant="danger" size="sm">Delete</Button>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="pagination">
                <Button variant="outline" size="sm" disabled>&lt;&lt;</Button>
                <Button variant="outline" size="sm" disabled>&lt;</Button>
                <span className="page-info">Page 1 of 5</span>
                <Button variant="outline" size="sm">&gt;</Button>
                <Button variant="outline" size="sm">&gt;&gt;</Button>
            </div>
        </div>
    );
}
