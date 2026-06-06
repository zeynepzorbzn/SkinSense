import { StyleSheet, Text, View } from 'react-native';

export default function GecmisEkrani() {
  return (
    <View style={styles.container}>
      <Text style={styles.baslik}>Geçmiş Analizler 📅</Text>
      <Text style={styles.metin}>Burada eski cilt analizlerini göreceksin.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f7fafc' },
  baslik: { fontSize: 24, fontWeight: 'bold', color: '#1a365d' },
  metin: { fontSize: 16, color: '#4a5568', marginTop: 10 }
});