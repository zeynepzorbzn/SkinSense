import { CameraView, useCameraPermissions } from 'expo-camera';
import { useRef, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function AnalizEkrani() {
  const [permission, requestPermission] = useCameraPermissions();
  const [analizSonucu, setAnalizSonucu] = useState<any>(null);
  const cameraRef = useRef<CameraView>(null);

  // --- İZİN KONTROLÜ VE BUTONU ---
  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.metin}>Kamera izni gerekiyor!</Text>
        <TouchableOpacity style={styles.buton} onPress={requestPermission}>
          <Text style={styles.butonMetin}>İzin Ver</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const fotografCek = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync();
      if (photo?.uri) {
        uploadToServer(photo.uri);
      }
    }
  };

  const uploadToServer = async (fileUri: string) => {
    let formData = new FormData();
    formData.append('file', { uri: fileUri, name: 'cilt.jpg', type: 'image/jpeg' } as any);
    formData.append('skin_type', 'Normal');
    formData.append('skin_concern', 'Yok');

    try {
      const response = await fetch('http://192.168.1.153:8000/analyze/image', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (!response.ok) {
        Alert.alert("Analiz Hatası", result.detail || "İçerik okunamadı.");
      } else {
        setAnalizSonucu(result.analiz_raporu);
      }
    } catch (error) {
      Alert.alert("Hata", "Backend'e ulaşılamadı.");
    }
  };

  // --- SONUÇ EKRANI ---
  if (analizSonucu) {
    return (
      <ScrollView contentContainerStyle={styles.resultContainer}>
        <Text style={styles.baslik}>Analiz Sonucun 🌿</Text>
        <Text style={styles.skor}>Uyum Skoru: {analizSonucu.uyum_skoru}/100</Text>
        
        <Text style={styles.altBaslik}>Öneriler:</Text>
        {analizSonucu.kisisel_uyarilar.map((u: string, i: number) => (
          <Text key={i} style={styles.listeMetni}>• {u}</Text>
        ))}

        <TouchableOpacity style={styles.buton} onPress={() => setAnalizSonucu(null)}>
          <Text style={styles.butonMetin}>Yeni Analiz Yap</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  // --- KAMERA EKRANI ---
  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} ref={cameraRef} facing="back" />
      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.buton} onPress={fotografCek}>
          <Text style={styles.butonMetin}>Fotoğrafı Yakala</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  camera: { flex: 1 },
  buttonContainer: { position: 'absolute', bottom: 50, left: 0, right: 0, alignItems: 'center' },
  resultContainer: { flexGrow: 1, padding: 30, backgroundColor: '#f7fafc', justifyContent: 'center' },
  baslik: { fontSize: 26, fontWeight: 'bold', color: '#1a365d', textAlign: 'center', marginBottom: 10 },
  skor: { fontSize: 20, textAlign: 'center', marginBottom: 20, color: '#3182ce', fontWeight: '600' },
  altBaslik: { fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  listeMetni: { fontSize: 16, color: '#4a5568', marginBottom: 5 },
  metin: { textAlign: 'center', marginTop: 100 },
  buton: { backgroundColor: '#3182ce', padding: 20, borderRadius: 30, marginTop: 20 },
  butonMetin: { color: 'white', fontWeight: 'bold', textAlign: 'center' }
});