import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // Backend'deki OAuth2 formatı için verileri özel bir formatta sarıyoruz
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await axios.post('http://127.0.0.1:8000/auth/login', params);
      
      // Gelen kapı kartını (token) tarayıcının güvenli hafızasına kaydet
      localStorage.setItem('token', response.data.access_token);
      navigate('/'); // Başarılıysa doğrudan Ana Sayfaya (Dashboard) ışınla
    } catch (err) {
      setError("❌ Giriş başarısız. Kullanıcı adı veya şifre hatalı.");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Tekrar Hoş Geldin! ✨</h2>
        <p style={styles.subtitle}>Güzellik analizlerine kaldığın yerden devam et.</p>
        
        <form onSubmit={handleLogin} style={styles.form}>
          <input 
            type="text" 
            placeholder="Kullanıcı Adı" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            style={styles.input} 
            required 
          />
          <input 
            type="password" 
            placeholder="Şifre" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            style={styles.input} 
            required 
          />
          <button type="submit" style={styles.button}>Giriş Yap</button>
        </form>
        {error && <p style={styles.error}>{error}</p>}
      </div>
    </div>
  );
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', marginTop: '50px' },
  card: { background: '#ffffff', padding: '40px', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)', width: '100%', maxWidth: '350px', textAlign: 'center' },
  title: { color: '#2d3748', margin: '0 0 10px 0', fontSize: '24px' },
  subtitle: { color: '#718096', fontSize: '14px', marginBottom: '30px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: { padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0', outline: 'none', backgroundColor: '#f8fafc', fontSize: '15px', color: '#4a5568' },
  button: { padding: '15px', borderRadius: '10px', border: 'none', backgroundColor: '#5C8374', color: '#ffffff', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', transition: 'background-color 0.3s' },
  error: { marginTop: '20px', color: '#e53e3e', fontWeight: '500', fontSize: '14px' }
};