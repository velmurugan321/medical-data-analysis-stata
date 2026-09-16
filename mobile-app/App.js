import React, { useState } from 'react';
import { SafeAreaView, View, Text, Pressable, StyleSheet, ScrollView, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { Ionicons } from '@expo/vector-icons';

const modules = [
  { title: 'Data Upload', icon: 'cloud-upload-outline', text: 'CSV, Excel and Stata' },
  { title: 'Variable View', icon: 'list-outline', text: 'Types, labels and missing' },
  { title: 'Descriptive', icon: 'stats-chart-outline', text: 'Frequency, mean, median' },
  { title: 'Diagnostic', icon: 'pulse-outline', text: 'Se, Sp, PPV, NPV, ROC' },
  { title: 'Regression', icon: 'git-branch-outline', text: 'Logistic, Poisson, Cox' },
  { title: 'Reports', icon: 'document-text-outline', text: 'Tables and export' }
];

export default function App() {
  const [file, setFile] = useState(null);

  async function pickData() {
    const result = await DocumentPicker.getDocumentAsync({
      type: ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/octet-stream'],
      copyToCacheDirectory: true
    });
    if (!result.canceled) {
      setFile(result.assets[0]);
      Alert.alert('Data selected', result.assets[0].name);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.eyebrow}>MEDICAL DATA ANALYSIS</Text>
            <Text style={styles.title}>Your analysis workspace</Text>
            <Text style={styles.subtitle}>Upload data and build reproducible statistical results.</Text>
          </View>
          <View style={styles.avatar}><Text style={styles.avatarText}>MD</Text></View>
        </View>

        <Pressable style={styles.upload} onPress={pickData}>
          <View style={styles.uploadIcon}><Ionicons name="cloud-upload-outline" size={28} color="#fff" /></View>
          <View style={{ flex: 1 }}>
            <Text style={styles.uploadTitle}>{file ? file.name : 'Upload your dataset'}</Text>
            <Text style={styles.uploadText}>{file ? 'Dataset selected — ready for analysis' : 'CSV • Excel • Stata'}</Text>
          </View>
          <Ionicons name="arrow-forward" size={22} color="#fff" />
        </Pressable>

        <Text style={styles.section}>Analysis modules</Text>
        <View style={styles.grid}>
          {modules.map((m) => (
            <Pressable key={m.title} style={styles.card} onPress={() => Alert.alert(m.title, 'This module is planned for the next build step.') }>
              <View style={styles.cardIcon}><Ionicons name={m.icon} size={22} color="#0f766e" /></View>
              <Text style={styles.cardTitle}>{m.title}</Text>
              <Text style={styles.cardText}>{m.text}</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.status}>
          <Ionicons name="shield-checkmark-outline" size={22} color="#0f766e" />
          <View style={{ flex: 1 }}>
            <Text style={styles.statusTitle}>Analysis-first design</Text>
            <Text style={styles.statusText}>Statistical calculations will be validated against R/Stata before production release.</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#f8fafc' },
  container: { padding: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 },
  eyebrow: { fontSize: 11, fontWeight: '800', letterSpacing: 1.4, color: '#0f766e', marginBottom: 6 },
  title: { fontSize: 27, fontWeight: '800', color: '#0f172a' },
  subtitle: { marginTop: 6, color: '#64748b', fontSize: 14, lineHeight: 20, maxWidth: 285 },
  avatar: { width: 44, height: 44, borderRadius: 14, backgroundColor: '#0f172a', alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '800' },
  upload: { backgroundColor: '#0f766e', borderRadius: 20, padding: 18, flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 28 },
  uploadIcon: { width: 50, height: 50, borderRadius: 15, backgroundColor: 'rgba(255,255,255,.18)', alignItems: 'center', justifyContent: 'center' },
  uploadTitle: { color: '#fff', fontSize: 16, fontWeight: '800' },
  uploadText: { color: '#ccfbf1', marginTop: 4, fontSize: 12 },
  section: { fontSize: 18, fontWeight: '800', color: '#0f172a', marginBottom: 14 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  card: { width: '47.8%', backgroundColor: '#fff', borderRadius: 18, padding: 16, minHeight: 145, borderWidth: 1, borderColor: '#e2e8f0' },
  cardIcon: { width: 42, height: 42, borderRadius: 13, backgroundColor: '#ccfbf1', alignItems: 'center', justifyContent: 'center', marginBottom: 13 },
  cardTitle: { fontSize: 15, fontWeight: '800', color: '#0f172a' },
  cardText: { fontSize: 12, color: '#64748b', marginTop: 5, lineHeight: 17 },
  status: { marginTop: 20, padding: 16, borderRadius: 18, backgroundColor: '#ecfdf5', flexDirection: 'row', gap: 12 },
  statusTitle: { fontWeight: '800', color: '#115e59' },
  statusText: { color: '#475569', fontSize: 12, lineHeight: 17, marginTop: 3 }
});
