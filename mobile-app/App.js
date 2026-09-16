import React, { useMemo, useState } from 'react';
import { SafeAreaView, View, Text, Pressable, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import { Ionicons } from '@expo/vector-icons';

const modules = [
  { title: 'Data Upload', icon: 'cloud-upload-outline', text: 'CSV and Excel now supported' },
  { title: 'Variable View', icon: 'list-outline', text: 'Types, missing and unique values' },
  { title: 'Descriptive', icon: 'stats-chart-outline', text: 'Frequency, mean, median and SD' },
  { title: 'Diagnostic', icon: 'pulse-outline', text: 'Sensitivity, specificity, PPV, NPV' },
  { title: 'Regression', icon: 'git-branch-outline', text: 'Logistic, Poisson and Cox' },
  { title: 'Reports', icon: 'document-text-outline', text: 'Publication-ready tables' }
];

function cleanValue(value) {
  if (value === null || value === undefined) return null;
  const s = String(value).trim();
  return s === '' || ['na', 'n/a', 'null', '.'].includes(s.toLowerCase()) ? null : s;
}

function summarize(rows) {
  if (!rows.length) return [];
  const columns = Object.keys(rows[0]);
  return columns.map((name) => {
    const values = rows.map((r) => cleanValue(r[name]));
    const nonMissing = values.filter((v) => v !== null);
    const numeric = nonMissing.filter((v) => /^-?(?:\d+\.?\d*|\.\d+)$/.test(v)).map(Number);
    const isNumeric = numeric.length > 0 && numeric.length / nonMissing.length >= 0.8;
    const mean = isNumeric ? numeric.reduce((a, b) => a + b, 0) / numeric.length : null;
    const variance = isNumeric && numeric.length > 1 ? numeric.reduce((a, b) => a + (b - mean) ** 2, 0) / (numeric.length - 1) : null;
    const sorted = isNumeric ? [...numeric].sort((a, b) => a - b) : [];
    const median = isNumeric ? sorted.length % 2 ? sorted[(sorted.length - 1) / 2] : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2 : null;
    return { name, type: isNumeric ? 'Numeric' : 'Categorical/Text', missing: values.length - nonMissing.length, unique: new Set(nonMissing).size, mean, sd: variance === null ? null : Math.sqrt(variance), median };
  });
}

export default function App() {
  const [file, setFile] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('dashboard');

  async function pickData() {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'],
        copyToCacheDirectory: true
      });
      if (result.canceled) return;
      setLoading(true);
      const asset = result.assets[0];
      const uri = asset.uri;
      const lower = asset.name.toLowerCase();
      let parsedRows = [];
      if (lower.endsWith('.csv')) {
        const text = await FileSystem.readAsStringAsync(uri);
        const parsed = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: false });
        parsedRows = parsed.data;
      } else if (lower.endsWith('.xlsx') || lower.endsWith('.xls')) {
        const base64 = await FileSystem.readAsStringAsync(uri, { encoding: FileSystem.EncodingType.Base64 });
        const workbook = XLSX.read(base64, { type: 'base64' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        parsedRows = XLSX.utils.sheet_to_json(firstSheet, { defval: '' });
      }
      const validRows = parsedRows.filter((r) => Object.keys(r).length > 0);
      setFile(asset);
      setRows(validRows);
      setTab('variables');
      Alert.alert('Dataset loaded', `${asset.name}\n${validRows.length.toLocaleString()} observations detected.`);
    } catch (error) {
      Alert.alert('Upload error', 'The dataset could not be read. Please check that it is a valid CSV or Excel file.');
    } finally {
      setLoading(false);
    }
  }

  const summary = useMemo(() => summarize(rows), [rows]);
  const numericVars = summary.filter((v) => v.type === 'Numeric');

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <View style={{ flex: 1 }}>
            <Text style={styles.eyebrow}>MEDICAL DATA ANALYSIS</Text>
            <Text style={styles.title}>Analysis workspace</Text>
            <Text style={styles.subtitle}>Import your dataset and inspect variables before statistical analysis.</Text>
          </View>
          <View style={styles.avatar}><Text style={styles.avatarText}>MD</Text></View>
        </View>

        <View style={styles.nav}>
          {['dashboard', 'variables', 'descriptive'].map((item) => (
            <Pressable key={item} onPress={() => setTab(item)} style={[styles.navItem, tab === item && styles.navActive]}>
              <Text style={[styles.navText, tab === item && styles.navTextActive]}>{item[0].toUpperCase() + item.slice(1)}</Text>
            </Pressable>
          ))}
        </View>

        <Pressable style={styles.upload} onPress={pickData} disabled={loading}>
          <View style={styles.uploadIcon}>{loading ? <ActivityIndicator color="#fff" /> : <Ionicons name="cloud-upload-outline" size={28} color="#fff" />}</View>
          <View style={{ flex: 1 }}>
            <Text style={styles.uploadTitle}>{file ? file.name : 'Upload your dataset'}</Text>
            <Text style={styles.uploadText}>{file ? `${rows.length.toLocaleString()} observations • ${summary.length} variables` : 'CSV • Excel'}</Text>
          </View>
          <Ionicons name="arrow-forward" size={22} color="#fff" />
        </Pressable>

        {tab === 'dashboard' && <>
          <Text style={styles.section}>Analysis modules</Text>
          <View style={styles.grid}>
            {modules.map((m, i) => (
              <Pressable key={m.title} style={styles.card} onPress={() => setTab(i === 0 ? 'dashboard' : i === 1 ? 'variables' : i === 2 ? 'descriptive' : 'dashboard')}>
                <View style={styles.cardIcon}><Ionicons name={m.icon} size={22} color="#0f766e" /></View>
                <Text style={styles.cardTitle}>{m.title}</Text>
                <Text style={styles.cardText}>{m.text}</Text>
              </Pressable>
            ))}
          </View>
        </>}

        {tab === 'variables' && <>
          <Text style={styles.section}>Variable View</Text>
          {!rows.length ? <Text style={styles.empty}>Upload a CSV or Excel dataset to see variables.</Text> : summary.map((v) => (
            <View key={v.name} style={styles.variableRow}>
              <View style={{ flex: 1 }}><Text style={styles.varName}>{v.name}</Text><Text style={styles.varMeta}>{v.type} • {v.unique} unique • {v.missing} missing</Text></View>
              {v.mean !== null && <View style={styles.metric}><Text style={styles.metricValue}>{v.mean.toFixed(2)}</Text><Text style={styles.metricLabel}>Mean</Text></View>}
            </View>
          ))}
        </>}

        {tab === 'descriptive' && <>
          <Text style={styles.section}>Descriptive Summary</Text>
          {!rows.length ? <Text style={styles.empty}>Upload a dataset first.</Text> : numericVars.map((v) => (
            <View key={v.name} style={styles.statCard}>
              <Text style={styles.varName}>{v.name}</Text>
              <View style={styles.statGrid}><Text>Mean: {v.mean.toFixed(2)}</Text><Text>SD: {v.sd?.toFixed(2) ?? '—'}</Text><Text>Median: {v.median.toFixed(2)}</Text><Text>Missing: {v.missing}</Text></View>
            </View>
          ))}
        </>}

        <View style={styles.status}><Ionicons name="shield-checkmark-outline" size={22} color="#0f766e" /><View style={{ flex: 1 }}><Text style={styles.statusTitle}>Validation-first</Text><Text style={styles.statusText}>Statistical methods will be validated against R/Stata before production release.</Text></View></View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#f8fafc' }, container: { padding: 20, paddingBottom: 40 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18 }, eyebrow: { fontSize: 11, fontWeight: '800', letterSpacing: 1.4, color: '#0f766e', marginBottom: 6 }, title: { fontSize: 27, fontWeight: '800', color: '#0f172a' }, subtitle: { marginTop: 6, color: '#64748b', fontSize: 14, lineHeight: 20, maxWidth: 290 },
  avatar: { width: 44, height: 44, borderRadius: 14, backgroundColor: '#0f172a', alignItems: 'center', justifyContent: 'center' }, avatarText: { color: '#fff', fontWeight: '800' },
  nav: { flexDirection: 'row', backgroundColor: '#e2e8f0', borderRadius: 14, padding: 4, marginBottom: 16 }, navItem: { flex: 1, paddingVertical: 9, alignItems: 'center', borderRadius: 10 }, navActive: { backgroundColor: '#fff' }, navText: { fontSize: 12, color: '#64748b', fontWeight: '700' }, navTextActive: { color: '#0f766e' },
  upload: { backgroundColor: '#0f766e', borderRadius: 20, padding: 18, flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 28 }, uploadIcon: { width: 50, height: 50, borderRadius: 15, backgroundColor: 'rgba(255,255,255,.18)', alignItems: 'center', justifyContent: 'center' }, uploadTitle: { color: '#fff', fontSize: 16, fontWeight: '800' }, uploadText: { color: '#ccfbf1', marginTop: 4, fontSize: 12 },
  section: { fontSize: 18, fontWeight: '800', color: '#0f172a', marginBottom: 14 }, grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 }, card: { width: '47.8%', backgroundColor: '#fff', borderRadius: 18, padding: 16, minHeight: 145, borderWidth: 1, borderColor: '#e2e8f0' }, cardIcon: { width: 42, height: 42, borderRadius: 13, backgroundColor: '#ccfbf1', alignItems: 'center', justifyContent: 'center', marginBottom: 13 }, cardTitle: { fontSize: 15, fontWeight: '800', color: '#0f172a' }, cardText: { fontSize: 12, color: '#64748b', marginTop: 5, lineHeight: 17 },
  variableRow: { backgroundColor: '#fff', borderRadius: 14, padding: 14, marginBottom: 8, borderWidth: 1, borderColor: '#e2e8f0', flexDirection: 'row', alignItems: 'center' }, varName: { fontSize: 14, fontWeight: '800', color: '#0f172a' }, varMeta: { fontSize: 11, color: '#64748b', marginTop: 4 }, metric: { alignItems: 'flex-end', minWidth: 60 }, metricValue: { fontSize: 16, fontWeight: '800', color: '#0f766e' }, metricLabel: { fontSize: 9, color: '#64748b' }, empty: { color: '#64748b', backgroundColor: '#fff', padding: 18, borderRadius: 14 }, statCard: { backgroundColor: '#fff', padding: 16, borderRadius: 14, marginBottom: 10, borderWidth: 1, borderColor: '#e2e8f0' }, statGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginTop: 10 }, status: { marginTop: 20, padding: 16, borderRadius: 18, backgroundColor: '#ecfdf5', flexDirection: 'row', gap: 12 }, statusTitle: { fontWeight: '800', color: '#115e59' }, statusText: { color: '#475569', fontSize: 12, lineHeight: 17, marginTop: 3 }
});
