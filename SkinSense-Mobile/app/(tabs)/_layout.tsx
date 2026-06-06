import { Tabs } from 'expo-router';
import { Text } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#3182ce' }}>
      <Tabs.Screen 
        name="index" 
        options={{ 
          title: 'Analiz', 
          tabBarIcon: () => <Text>🔍</Text> 
        }} 
      />
      <Tabs.Screen 
        name="gecmis" 
        options={{ 
          title: 'Geçmiş', 
          tabBarIcon: () => <Text>📅</Text> 
        }} 
      />
    </Tabs>
  );
}