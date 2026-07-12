import { Link, useParams } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import './AnalysisResult.css';

export default function AnalysisResult() {
    const { id } = useParams();

    return (
        <div className="analysis-result-page">
            <h1>Analysis Result {id && <span className="subtitle">#{id}</span>}</h1>

            <div className="result-sections">
                <Card className="result-card translate-card">
                    <h3>Translation</h3>
                    <p>회사의 새로운 시장으로의 -------은 성공적이었다.</p>
                </Card>

                <Card className="result-card correct-card">
                    <h3>Correct Answer</h3>
                    <div className="answer-highlight green">
                        <span className="choice-badge">B</span>
                        <span className="choice-text">expansion (명사)</span>
                    </div>
                    <p className="explanation">전치사 to 앞, 소유격 's 뒤이므로 명사가 올 자리입니다. 'expansion'은 '확장'이라는 뜻의 명사입니다.</p>
                </Card>

                <Card className="result-card wrong-card">
                    <h3>Why Your Answer is Wrong</h3>
                    <div className="answer-highlight orange">
                        <span className="choice-badge">C</span>
                        <span className="choice-text">expansive (형용사)</span>
                    </div>
                    <p className="explanation">형용사는 소유격 뒤에 올 수 있지만, 그 뒤에 꾸며줄 명사가 있어야 합니다. 빈칸 뒤에는 명사가 없으므로 오답입니다.</p>
                </Card>

                <Card className="result-card error-type-card">
                    <h3>Error Category</h3>
                    <span className="badge badge-blue mb-2">Part of Speech Error</span>
                    <p className="explanation">빈칸에 품사가 들어갈 자리를 정확히 파악하지 못했습니다.</p>
                </Card>

                <Card className="result-card learning-card">
                    <h3>Key Learning Point</h3>
                    <p className="mb-2"><strong>소유격(my, his, the company's 등) 뒤에는 명사가 필요합니다.</strong></p>
                    <div className="examples">
                        <div className="example-item">
                            <p className="en">Her dedication to the project impressed everyone.</p>
                            <p className="ko">그녀의 프로젝트에 대한 헌신은 모두에게 감동을 주었다.</p>
                        </div>
                    </div>
                </Card>

                <Card className="result-card vocab-card">
                    <h3>Vocabulary</h3>
                    <table className="vocab-table">
                        <thead>
                            <tr>
                                <th>Word</th>
                                <th>Part of Speech</th>
                                <th>Meaning</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>expansion</td>
                                <td>noun</td>
                                <td>확장, 확대</td>
                            </tr>
                            <tr>
                                <td>expansive</td>
                                <td>adjective</td>
                                <td>광범위한</td>
                            </tr>
                        </tbody>
                    </table>
                </Card>
            </div>

            <div className="confidence-score">
                Confidence Score: <strong>95%</strong>
            </div>

            <div className="bottom-actions">
                <Button size="lg">Save to Notes</Button>
                <Link to="/analyze">
                    <Button variant="outline" size="lg">Analyze Another</Button>
                </Link>
            </div>
        </div>
    );
}
