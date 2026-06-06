import { useState, useEffect } from 'react';
import axios from 'axios';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Sayfa açılır açılmaz geçmişi API'den çek
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return; // Giriş yapılmamışsa hiçbir şey yapma
        }
        
        const response = await axios.get('http://127.0.0.1:8000/history/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setHistory(response.data.reverse()); // En son okutulan en üstte görünsün diye ters çeviriyoruz
      } catch (error) {
        console.error("Geçmiş yüklenemedi", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Geçmiş Taramalarım 🌿</h2>
      <p style={styles.subtitle}>Daha önce analiz ettiğin ürünler ve uyum skorların.</p>

      {loading ? (
        <p style={{ color: '#718096' }}>Geçmişin yükleniyor...</p>
      ) : history.length === 0 ? (
        <div style={styles.emptyBox}>
          <p>Henüz bir ürün taramadın. Hadi ilk ürününü analiz et!</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {history.map((item, index) => (
            <div key={index} style={styles.card}>
             <h3 style={styles.productName}>{item.urun_adi}</h3>
<p style={styles.barcode}>Tarih: {new Date(item.tarih).toLocaleDateString('tr-TR')}</p> {/* Tarihi okunaklı yapar */}
<div style={styles.scoreBadge(item.uyum_skoru)}>
  Uyum Skoru: {item.uyum_skoru}
</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Tasarım Objeleri (Clean Vibe)
const styles = {
  container: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '30px', padding: '0 20px' },
  title: { color: '#2d3748', margin: '0 0 10px 0', fontSize: '26px' },
  subtitle: { color: '#718096', fontSize: '15px', marginBottom: '30px' },
  emptyBox: { background: '#ffffff', padding: '30px', borderRadius: '12px', color: '#718096', border: '1px dashed #cbd5e0' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px', width: '100%', maxWidth: '900px' },
  card: { background: '#ffffff', padding: '25px', borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.03)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' },
  productName: { color: '#2d3748', margin: '0 0 10px 0', fontSize: '18px', lineHeight: '1.4' },
  barcode: { color: '#a0aec0', fontSize: '13px', margin: '0 0 20px 0' },
  scoreBadge: (skor) => ({
    alignSelf: 'flex-start',
    backgroundColor: skor >= 70 ? '#F0FFF4' : (skor >= 40 ? '#FFFFF0' : '#FFF5F5'),
    color: skor >= 70 ? '#276749' : (skor >= 40 ? '#975A16' : '#9B2C2C'),
    padding: '8px 15px',
    borderRadius: '20px',
    fontWeight: 'bold',
    fontSize: '14px',
    border: `1px solid ${skor >= 70 ? '#9AE6B4' : (skor >= 40 ? '#F6E05E' : '#FEB2B2')}`
  })
};