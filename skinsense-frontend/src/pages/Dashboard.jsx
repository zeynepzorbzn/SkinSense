import { useState } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('barcode'); 
  const [barcode, setBarcode] = useState('');
  const [productName, setProductName] = useState('');
  const [manualIngredients, setManualIngredients] = useState('');
  const [imageFile, setImageFile] = useState(null);
  
  const [skinType, setSkinType] = useState('Normal');
  const [skinConcern, setSkinConcern] = useState('Yok'); // YENİ: CİLT PROBLEMİ STATE'İ
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeProduct = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const token = localStorage.getItem('token'); 
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      let response;
      
      if (activeTab === 'barcode') {
        response = await axios.post('http://127.0.0.1:8000/analyze/barcode', {
          barcode: barcode,
          skin_type: skinType,
          skin_concern: skinConcern
        }, { headers });
      } else if (activeTab === 'name') {
        response = await axios.post('http://127.0.0.1:8000/analyze/name', {
          product_name: productName,
          skin_type: skinType,
          skin_concern: skinConcern
        }, { headers });
      } else if (activeTab === 'manual') {
        response = await axios.post('http://127.0.0.1:8000/analyze/manual', {
          ingredients: manualIngredients,
          skin_type: skinType,
          skin_concern: skinConcern
        }, { headers });
      } else if (activeTab === 'image') {
        if (!imageFile) {
          setError("Lütfen analiz için bir fotoğraf seçin.");
          setLoading(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", imageFile);
        formData.append("skin_type", skinType);
        formData.append("skin_concern", skinConcern);
        
        response = await axios.post('http://127.0.0.1:8000/analyze/image', formData, { headers });
      }
      
      setResult(response.data);

    } catch (err) {
      setError(err.response?.data?.detail || "Sunucuya bağlanılamadı veya analiz başarısız.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.searchCard}>
        <h2 style={styles.title}>Yeni Ürün Analizi 🌿</h2>
        
        <div style={styles.tabContainer}>
        <button style={activeTab === 'name' ? styles.activeTab : styles.inactiveTab} onClick={() => {setActiveTab('name'); setError(null); setResult(null);}}>Ürün Adı</button>
          <button style={activeTab === 'barcode' ? styles.activeTab : styles.inactiveTab} onClick={() => {setActiveTab('barcode'); setError(null); setResult(null);}}>Barkod</button>
          <button style={activeTab === 'manual' ? styles.activeTab : styles.inactiveTab} onClick={() => {setActiveTab('manual'); setError(null); setResult(null);}}>İçerik</button>
          <button style={activeTab === 'image' ? styles.activeTab : styles.inactiveTab} onClick={() => {setActiveTab('image'); setError(null); setResult(null);}}>📸 Fotoğraf</button>
        </div>
        
        <form onSubmit={analyzeProduct} style={styles.form}>
          
          {/* YENİ: Ürün Adı İçin Kutucuk */}
          {activeTab === 'name' && (
            <input 
              type="text" 
              placeholder="Ürün adı (Örn: CeraVe Moisturizing Cream)" 
              value={productName} 
              onChange={(e) => setProductName(e.target.value)} 
              style={styles.input} 
              required 
            />
          )}

          {/* Barkod Kutucuğu */}
          {activeTab === 'barcode' && (
            <input 
              type="text" 
              placeholder="Barkod (Örn: 3606000537675)" 
              value={barcode} 
              onChange={(e) => setBarcode(e.target.value)} 
              style={styles.input} 
              required 
            />
          )}

          {/* İçerik Listesi Kutucuğu */}
          {activeTab === 'manual' && (
            <textarea 
              placeholder="İçerik listesini yapıştırın..." 
              value={manualIngredients} 
              onChange={(e) => setManualIngredients(e.target.value)} 
              style={{...styles.input, height: '80px', resize: 'vertical'}} 
              required 
            />
          )}

          {/* Fotoğraf Kutucuğu */}
          {activeTab === 'image' && (
            <input 
              type="file" 
              accept="image/*" 
              onChange={(e) => setImageFile(e.target.files[0])} 
              style={{...styles.input, padding: '10px'}} 
              required 
            />
          )}

          {/* CİLT TİPİ SEÇİMİ */}
          <select value={skinType} onChange={(e) => setSkinType(e.target.value)} style={styles.input}>
            <option value="Normal">Normal Cilt</option>
            <option value="Kuru">Kuru Cilt</option>
            <option value="Yağlı">Yağlı Cilt</option>
            <option value="Karma">Karma Cilt</option>
            <option value="Hassas">Hassas Cilt</option>
          </select>

          {/* YENİ EKLENEN: CİLT PROBLEMİ SEÇİMİ */}
          <select value={skinConcern} onChange={(e) => setSkinConcern(e.target.value)} style={styles.input}>
            <option value="Yok">Ekstra Cilt Problemim Yok</option>
            <option value="Akne/Sivilce">Akne / Sivilce Eğilimi</option>
            <option value="Leke/Renk Eşitsizliği">Leke / Renk Eşitsizliği</option>
            <option value="Kırışıklık/Yaşlanma">Kırışıklık / Yaşlanma</option>
          </select>

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Zeka Analiz Ediyor..." : "Analizi Başlat"}
          </button>
        </form>
        {error && <p style={styles.error}>{error}</p>}
      </div>

      {/* SONUÇ KARTLARI BURADAN AŞAĞISI AYNI */}
      {result && (
        <div style={styles.resultCard}>
          <h2 style={{ color: '#2d3748', marginTop: 0 }}>{result.urun_adi}</h2>
          <p style={{ color: '#718096', fontSize: '15px' }}>Marka: <strong>{result.marka}</strong></p>
          
          <div style={styles.scoreBox(result.analiz_raporu.uyum_skoru)}>
            <span style={{ fontSize: '14px', fontWeight: 'bold' }}>Cilt Uyum Skoru</span>
            <span style={{ fontSize: '32px', fontWeight: '900' }}>{result.analiz_raporu.uyum_skoru}/100</span>
          </div>

          {result.analiz_raporu.kisisel_uyarilar?.length > 0 && (
            <div style={styles.warningBox}>
              <h4 style={{ margin: '0 0 10px 0', color: '#2d3748' }}>💡 Sana Özel Yorumlar</h4>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#4a5568', fontSize: '14px' }}>
                {result.analiz_raporu.kisisel_uyarilar.map((uyari, index) => (
                  <li key={index} style={{ marginBottom: '5px' }}>{uyari}</li>
                ))}
              </ul>
            </div>
          )}

          {result.analiz_raporu.icerik_detaylari && (
            <div style={{ marginTop: '30px' }}>
              <h4 style={{ color: '#2d3748', marginBottom: '15px', borderBottom: '2px solid #e2e8f0', paddingBottom: '10px' }}>
                🔬 İçerik İncelemesi
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {result.analiz_raporu.icerik_detaylari.map((icerik, index) => (
                  <div key={index} style={{ 
                    padding: '15px', borderRadius: '10px', backgroundColor: '#f8fafc',
                    borderLeft: `4px solid ${icerik.risk_seviyesi === 'Yüksek' ? '#F56565' : icerik.risk_seviyesi === 'Orta' ? '#ECC94B' : icerik.risk_seviyesi === 'Düşük' ? '#48BB78' : '#A0AEC0'}`
                  }}>
                    <strong style={{ color: '#2d3748', fontSize: '15px' }}>{icerik.madde_adi}</strong>
                    <p style={{ margin: '5px 0 0 0', fontSize: '13px', color: '#718096' }}>{icerik.degerlendirme}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { display: 'flex', flexWrap: 'wrap', gap: '30px', justifyContent: 'center', marginTop: '30px', padding: '0 20px', paddingBottom: '50px' },
  searchCard: { background: '#ffffff', padding: '40px', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)', width: '100%', maxWidth: '400px', height: 'fit-content' },
  resultCard: { background: '#ffffff', padding: '40px', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.04)', width: '100%', maxWidth: '550px' },
  title: { color: '#2d3748', margin: '0 0 20px 0', fontSize: '22px' },
  tabContainer: { display: 'flex', marginBottom: '20px', backgroundColor: '#edf2f7', borderRadius: '10px', padding: '4px' },
  activeTab: { flex: 1, padding: '8px', border: 'none', borderRadius: '8px', backgroundColor: '#ffffff', color: '#2d3748', fontWeight: 'bold', fontSize: '14px', cursor: 'pointer', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
  inactiveTab: { flex: 1, padding: '8px', border: 'none', backgroundColor: 'transparent', color: '#718096', fontWeight: '500', fontSize: '14px', cursor: 'pointer' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: { padding: '14px', borderRadius: '10px', border: '1px solid #e2e8f0', outline: 'none', backgroundColor: '#f8fafc', fontSize: '15px', color: '#4a5568' },
  button: { padding: '15px', borderRadius: '10px', border: 'none', backgroundColor: '#5C8374', color: '#ffffff', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' },
  error: { marginTop: '15px', color: '#e53e3e', fontWeight: '500', fontSize: '14px' },
  warningBox: { backgroundColor: '#F7FAFC', padding: '20px', borderRadius: '10px', borderLeft: '4px solid #4FD1C5', marginTop: '20px' },
  scoreBox: (skor) => ({ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: skor >= 70 ? '#F0FFF4' : (skor >= 40 ? '#FFFFF0' : '#FFF5F5'), color: skor >= 70 ? '#276749' : (skor >= 40 ? '#975A16' : '#9B2C2C'), padding: '20px', borderRadius: '12px', border: `2px solid ${skor >= 70 ? '#9AE6B4' : (skor >= 40 ? '#F6E05E' : '#FEB2B2')}`, marginTop: '20px' })
};