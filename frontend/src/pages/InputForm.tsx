import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import './InputForm.css';

export default function InputForm() {
    const navigate = useNavigate();
    const [testType, setTestType] = useState('RC');
    const [part, setPart] = useState(5);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Simulate API call and redirect to result
        navigate('/result/demo-id');
    };

    return (
        <div className="input-form-page">
            <h1>New Wrong Note Analysis</h1>

            <Card>
                <form onSubmit={handleSubmit}>
                    <div className="form-group type-toggle">
                        <button
                            type="button"
                            className={`toggle-btn ${testType === 'LC' ? 'active' : ''}`}
                            onClick={() => setTestType('LC')}
                        >LC (Listening)</button>
                        <button
                            type="button"
                            className={`toggle-btn ${testType === 'RC' ? 'active' : ''}`}
                            onClick={() => setTestType('RC')}
                        >RC (Reading)</button>
                    </div>

                    <div className="form-group part-selector">
                        {[1, 2, 3, 4, 5, 6, 7].map(p => (
                            <button
                                key={p}
                                type="button"
                                className={`pill-btn ${part === p ? 'active' : ''}`}
                                onClick={() => setPart(p)}
                            >
                                Part {p}
                            </button>
                        ))}
                    </div>

                    <div className="form-group">
                        <label className="form-label">Question Text</label>
                        <textarea className="form-control" placeholder="Enter the question here..." required></textarea>
                    </div>

                    <div className="choices-grid">
                        <div className="form-group">
                            <label className="form-label">Choice A</label>
                            <input type="text" className="form-control" placeholder="Enter choice A..." required />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Choice B</label>
                            <input type="text" className="form-control" placeholder="Enter choice B..." required />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Choice C</label>
                            <input type="text" className="form-control" placeholder="Enter choice C..." required />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Choice D</label>
                            <input type="text" className="form-control" placeholder="Enter choice D..." required />
                        </div>
                    </div>

                    <div className="answers-grid">
                        <div className="form-group">
                            <label className="form-label">Your Answer</label>
                            <select className="form-control" required>
                                <option value="">Select choice...</option>
                                <option value="A">Choice A</option>
                                <option value="B">Choice B</option>
                                <option value="C">Choice C</option>
                                <option value="D">Choice D</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Correct Answer</label>
                            <select className="form-control" required>
                                <option value="">Select choice...</option>
                                <option value="A">Choice A</option>
                                <option value="B">Choice B</option>
                                <option value="C">Choice C</option>
                                <option value="D">Choice D</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Why did you choose this answer? (optional)</label>
                        <textarea className="form-control" placeholder="Describe your reasoning..." style={{ minHeight: '80px' }}></textarea>
                    </div>

                    <Button type="submit" size="lg" fullWidth>Start Analysis</Button>
                </form>
            </Card>
        </div>
    );
}
