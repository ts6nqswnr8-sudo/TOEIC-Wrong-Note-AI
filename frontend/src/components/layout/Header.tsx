import { Link, useLocation } from 'react-router-dom';
import { BookOpen } from 'lucide-react';
import './Header.css';

export default function Header() {
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/' },
        { name: 'Analyze', path: '/analyze' },
        { name: 'Notes', path: '/notes' },
        { name: 'Stats', path: '/stats' }
    ];

    return (
        <header className="header">
            <div className="container header-container">
                <Link to="/" className="logo">
                    <BookOpen className="logo-icon" size={24} />
                    <span className="logo-text">TOEIC Wrong Note AI</span>
                </Link>

                <nav className="nav">
                    {navItems.map(item => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                        >
                            {item.name}
                        </Link>
                    ))}
                </nav>
            </div>
        </header>
    );
}
