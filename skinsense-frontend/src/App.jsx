import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import History from './pages/History'; 
function App() {
  return (
    <Router>
      <div className="App">
        {/* Üst Menü (Navbar) */}
        <nav style={{ padding: '20px', background: '#1a1a1a', marginBottom: '30px', borderRadius: '8px' }}>
          <h2 style={{ display: 'inline', color: '#646cff', marginRight: '40px' }}>SkinSense AI</h2>
          <Link to="/" style={{ marginRight: '20px', color: 'white', textDecoration: 'none' }}>Analiz Merkezi</Link>
          <Link to="/login" style={{ marginRight: '20px', color: 'white', textDecoration: 'none' }}>Giriş Yap</Link>
          <Link to="/register" style={{ marginRight: '20px', color: 'white', textDecoration: 'none' }}>Kayıt Ol</Link>
          <Link to="/history" style={{ marginRight: '20px', color: '#a0aec0', textDecoration: 'none', fontWeight: '500' }}>Geçmiş</Link>

        </nav>

        {/* Sayfa İçeriklerinin Değiştiği Alan */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;