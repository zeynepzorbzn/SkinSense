import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [skinType, setSkinType] = useState('Normal');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault(); // Sayfanın yenilenmesini engeller
    try {
      await axios.post('http://127.0.0.1:8000/auth/register', {
        username: username,
        password: password,
        skin_type: skinType
      });
      setMessage("🌿 Harika! Hesabın oluşturuldu. Giriş sayfasına yönlendiriliyorsun...");
      setTimeout(() => navigate('/login'), 2500); // 2.5 saniye sonra Login'e atar
    } catch (error) {
      setMessage("❌ " + (error.response?.data?.detail || "Bir hata oluştu."));
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Aramıza Katıl</h2>
        <p style={styles.subtitle}>Cildine en uygun ürünleri keşfetmeye başla.</p>
        
        <form onSubmit={handleRegister} style={styles.form}>
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
          <select value={skinType} onChange={(e) => setSkinType(e.target.value)} style={styles.input}>
            <option value="Normal">Normal Cilt</option>
            <option value="Kuru">Kuru Cilt</option>
            <option value="Yağlı">Yağlı Cilt</option>
            <option value="Karma">Karma Cilt</option>
            <option value="Hassas">Hassas Cilt</option>
          </select>

          <button type="submit" style={styles.button}>Kayıt Ol</button>
        </form>
        {message && <p style={styles.message}>{message}</p>}
      </div>
    </div>
  );
}

// Tasarım (Clean Vibe) Objeleri
const styles = {
  container: { display: 'flex', justifyContent: 'center', marginTop: '50px' },
  card: { background: '#ffffff', padding: '40px', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)', width: '100%', maxWidth: '350px', textAlign: 'center' },
  title: { color: '#2d3748', margin: '0 0 10px 0', fontSize: '24px' },
  subtitle: { color: '#718096', fontSize: '14px', marginBottom: '30px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: { padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0', outline: 'none', backgroundColor: '#f8fafc', fontSize: '15px', color: '#4a5568' },
  button: { padding: '15px', borderRadius: '10px', border: 'none', backgroundColor: '#5C8374', color: '#ffffff', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', transition: 'background-color 0.3s' },
  message: { marginTop: '20px', color: '#5C8374', fontWeight: '500', fontSize: '14px' }
};