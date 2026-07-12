import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import InputForm from './pages/InputForm';
import AnalysisResult from './pages/AnalysisResult';
import NotesHistory from './pages/NotesHistory';
import WeaknessAnalysis from './pages/WeaknessAnalysis';

function App() {
    return (
        <BrowserRouter>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/analyze" element={<InputForm />} />
                    <Route path="/result/:id" element={<AnalysisResult />} />
                    <Route path="/notes" element={<NotesHistory />} />
                    <Route path="/stats" element={<WeaknessAnalysis />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Layout>
        </BrowserRouter>
    );
}

export default App;
