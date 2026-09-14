import { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Module = 'dashboard' | 'upload' | 'variables' | 'quality' | 'descriptive' | 'table1' | 'association' | 'regression' | 'diagnostic' | 'roc' | 'graphs' | 'results'
type Info = { filename?: string; rows: number; columns: number; variables: Array<Record<string, unknown>> }

type ApiResponse = Record<string, unknown>

const modules: Array<{ id: Module; label: string; icon: string }> = [
  { id: 'dashboard', label: 'Dashboard', icon: '▦' },
  { id: 'upload', label: 'Data Upload', icon: '⇧' },
  { id: 'variables', label: 'Variable View', icon: '☷' },
  { id: 'quality', label: 'Data Quality', icon: '✓' },
  { id: 'descriptive', label: 'Descriptive', icon: '▤' },
  { id: 'table1', label: 'Table 1', icon: '▥' },
  { id: 'association', label: 'Association', icon: '↔' },
  { id: 'regression', label: 'Regression', icon: 'β' },
  { id: 'diagnostic', label: 'Diagnostic', icon: '⊞' },
  { id: 'roc', label: 'ROC Analysis', icon: '⌁' },
  { id: 'graphs', label: 'Graphs', icon: '◒' },
  { id: 'results', label: 'Results & Export', icon: '⇩' }
]

function getInitialApi() {
  return localStorage.getItem('medicalAnalyticsApi') || ''
}

function App() {
  const [active, setActive] = useState<Module>('dashboard')
  const [file, setFile] = useState<File | null>(null)
  const [info, setInfo] = useState<Info | null>(null)
  const [quality, setQuality] = useState<unknown>(null)
  const [result, setResult] = useState<unknown>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('No dataset loaded')
  const [apiUrl, setApiUrl] = useState(getInitialApi)
  const [apiStatus, setApiStatus] = useState<'unknown' | 'ok' | 'error'>('unknown')

  const API = apiUrl.replace(/\/$/, '')

  useEffect(() => {
    if (!API) return
    fetch(`${API}/health`).then((r) => { if (!r.ok) throw new Error(); setApiStatus('ok') }).catch(() => setApiStatus('error'))
  }, [API])

  function saveApiUrl(value: string) {
    setApiUrl(value)
    localStorage.setItem('medicalAnalyticsApi', value.trim())
    setApiStatus('unknown')
  }

  async function post(path: string, fields: Record<string, string> = {}) {
    if (!file) throw new Error('Upload a dataset first.')
    if (!API) throw new Error('Configure the backend API URL in the top bar before running analysis.')
    const form = new FormData()
    form.append('file', file)
    Object.entries(fields).forEach(([key, value]) => form.append(key, value))
    const response = await fetch(`${API}${path}`, { method: 'POST', body: form })
    const text = await response.text()
    if (!response.ok) throw new Error(text || `Request failed (${response.status})`)
    return JSON.parse(text) as ApiResponse
  }

  async function loadDataset(next: File) {
    setFile(next); setBusy(true); setMessage('Inspecting dataset...')
    try {
      const inspected = await post('/api/v1/data/inspect') as unknown as Info
      setInfo(inspected)
      const checked = await post('/api/v1/data/quality')
      setQuality(checked.results)
      setMessage('Dataset loaded and quality checked')
      setActive('dashboard')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'API error')
    } finally { setBusy(false) }
  }

  async function runAnalysis(path: string, fields: Record<string, string>) {
    setBusy(true); setMessage('Running analysis...')
    try { setResult(await post(path, fields)); setActive('results'); setMessage('Analysis completed') }
    catch (error) { setResult({ error: error instanceof Error ? error.message : 'Analysis failed' }); setActive('results'); setMessage('Analysis failed') }
    finally { setBusy(false) }
  }

  const variables = useMemo(() => info?.variables.map((v) => String(v.name)) || [], [info])
  const title = modules.find((item) => item.id === active)?.label || 'Dashboard'

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">M</div><div><strong>Medical Analytics Lab</strong><span>Clinical statistics platform</span></div></div>
        <nav>{modules.map((item) => <button key={item.id} className={active === item.id ? 'active' : ''} onClick={() => setActive(item.id)}><i>{item.icon}</i>{item.label}</button>)}</nav>
        <div className="side-footer"><span className={`dot ${apiStatus === 'error' ? 'bad' : ''}`} /> {API ? (apiStatus === 'ok' ? 'Statistical engine connected' : apiStatus === 'error' ? 'API connection failed' : 'Checking statistical engine...') : 'Backend API not configured'}</div>
      </aside>
      <main className="main">
        <header>
          <div><span className="eyebrow">Medical statistics</span><h1>{title}</h1><p>Upload data, inspect variables, run validated clinical analyses and export results.</p></div>
          <label className="primary">+ Upload Dataset<input hidden type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={(event) => event.target.files?.[0] && loadDataset(event.target.files[0])} /></label>
        </header>
        <div className="api-bar"><span>Backend API</span><input value={apiUrl} onChange={(e) => saveApiUrl(e.target.value)} placeholder="https://your-backend.example.com" /><span className={`api-state ${apiStatus}`}>{apiStatus === 'ok' ? '● Connected' : apiStatus === 'error' ? '● Error' : '● Not checked'}</span></div>
        {active === 'dashboard' && <Dashboard info={info} message={message} busy={busy} onUpload={() => setActive('upload')} onRun={() => info && setActive('descriptive')} />}
        {active === 'upload' && <Upload file={file} busy={busy} message={message} onUpload={loadDataset} />}
        {active === 'variables' && <Panel title="Variable View">{info ? <VariableTable variables={info.variables} /> : <Empty text="Upload a dataset to inspect variables." />}</Panel>}
        {active === 'quality' && <Panel title="Data Quality">{quality ? <pre className="result">{JSON.stringify(quality, null, 2)}</pre> : <Empty text="Upload a dataset to run quality checks." />}</Panel>}
        {active === 'descriptive' && <VariableAnalysis title="Descriptive Analysis" variables={variables} multi onRun={(v) => runAnalysis('/api/v1/analysis/descriptive', { variables: v.join(',') })} busy={busy} />}
        {active === 'table1' && <TableOneAnalysis variables={variables} onRun={(v) => runAnalysis('/api/v1/analysis/table-one', { variables: v.variables.join(','), group: v.group })} busy={busy} />}
        {active === 'association' && <PairAnalysis title="Categorical Association" firstLabel="Variable" secondLabel="Outcome" variables={variables} onRun={(v) => runAnalysis('/api/v1/analysis/association', { variable: v.first, outcome: v.second })} busy={busy} />}
        {active === 'diagnostic' && <PairAnalysis title="Diagnostic Accuracy" firstLabel="Index test" secondLabel="Reference standard" variables={variables} onRun={(v) => runAnalysis('/api/v1/analysis/diagnostic', { index_test: v.first, reference_standard: v.second })} busy={busy} />}
        {active === 'roc' && <PairAnalysis title="ROC Analysis" firstLabel="Test / predictor" secondLabel="Binary outcome" variables={variables} onRun={(v) => runAnalysis('/api/v1/analysis/roc', { test: v.first, outcome: v.second })} busy={busy} />}
        {active === 'regression' && <RegressionAnalysis variables={variables} onRun={(path, config) => runAnalysis(path, { config: JSON.stringify(config) })} busy={busy} />}
        {active === 'graphs' && <Panel title="Graphs"><Empty text="Graph modules are next: histogram, boxplot, bar chart, scatter, forest plot, ROC and Kaplan–Meier." /></Panel>}
        {active === 'results' && <Results result={result} />}
      </main>
    </div>
  )
}

function Dashboard({ info, message, busy, onUpload, onRun }: { info: Info | null; message: string; busy: boolean; onUpload: () => void; onRun: () => void }) {
  return <><div className="hero-grid"><div className="hero"><span className="badge">{busy ? 'PROCESSING' : info ? 'DATASET READY' : 'READY'}</span><h2>Clinical analysis, built for reproducibility.</h2><p>From raw dataset to publication-ready statistical results.</p><button className="primary" onClick={onUpload}>Upload your dataset</button>{info && <button className="secondary" onClick={onRun}>Start descriptive analysis</button>}</div><div className="pipeline"><span>WORKFLOW</span><div>Upload → Inspect → Quality → Analyze → Validate → Export</div><small>{message}</small></div></div><div className="cards"><Card label="Dataset" value={info?.filename || '—'} /><Card label="Rows" value={info ? String(info.rows) : '—'} /><Card label="Variables" value={info ? String(info.columns) : '—'} /><Card label="API" value="Backend required" /></div></>
}
function Card({ label, value }: { label: string; value: string }) { return <div className="card"><span>{label}</span><strong>{value}</strong></div> }
function Upload({ file, busy, message, onUpload }: { file: File | null; busy: boolean; message: string; onUpload: (file: File) => void }) { return <Panel title="Upload Dataset"><label className="drop"><b>{busy ? 'Inspecting...' : 'Choose your dataset'}</b><span>CSV, XLSX, XLS, Stata DTA or TSV</span><input type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])} /></label>{file && <div className="file-row"><b>{file.name}</b><em>{message}</em></div>}</Panel> }

function VariableTable({ variables }: { variables: Array<Record<string, unknown>> }) {
  return <div className="table-wrap"><table><thead><tr><th>Name</th><th>Type</th><th>Storage</th><th>N</th><th>Missing</th><th>Unique</th><th>Min</th><th>Max</th></tr></thead><tbody>{variables.map((v) => <tr key={String(v.name)}><td><b>{String(v.name)}</b></td><td>{String(v.type)}</td><td>{String(v.storage_type)}</td><td>{String(v.n)}</td><td>{String(v.missing)}</td><td>{String(v.unique)}</td><td>{v.min == null ? '—' : String(v.min)}</td><td>{v.max == null ? '—' : String(v.max)}</td></tr>)}</tbody></table></div>
}

function VariableAnalysis({ title, variables, multi, onRun, busy }: { title: string; variables: string[]; multi?: boolean; onRun: (v: string[]) => void; busy: boolean }) {
  const [selected, setSelected] = useState<string[]>([])
  return <Panel title={title}><p className="muted">Select one or more variables. Leave empty to analyse all variables.</p><select multiple={multi} value={selected} onChange={(e) => setSelected(Array.from(e.target.selectedOptions).map((o) => o.value))}>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select><button className="primary" disabled={busy} onClick={() => onRun(selected)}>{busy ? 'Running...' : 'Run Analysis'}</button></Panel>
}

function TableOneAnalysis({ variables, onRun, busy }: { variables: string[]; onRun: (v: { variables: string[]; group: string }) => void; busy: boolean }) {
  const [selected, setSelected] = useState<string[]>([]); const [group, setGroup] = useState('')
  return <Panel title="Publication-ready Table 1"><p className="muted">Choose analysis variables and optionally a grouping/outcome variable.</p><select multiple value={selected} onChange={(e) => setSelected(Array.from(e.target.selectedOptions).map((o) => o.value))}>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select><label className="field"><span>Group variable (optional)</span><select value={group} onChange={(e) => setGroup(e.target.value)}><option value="">Overall only</option>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select></label><button className="primary" disabled={busy} onClick={() => onRun({ variables: selected, group })}>{busy ? 'Running...' : 'Generate Table 1'}</button></Panel>
}

function PairAnalysis({ title, firstLabel, secondLabel, variables, onRun, busy }: { title: string; firstLabel: string; secondLabel: string; variables: string[]; onRun: (v: { first: string; second: string }) => void; busy: boolean }) {
  const [first, setFirst] = useState(''); const [second, setSecond] = useState('')
  return <Panel title={title}><div className="two-col"><label className="field"><span>{firstLabel}</span><select value={first} onChange={(e) => setFirst(e.target.value)}><option value="">Select</option>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select></label><label className="field"><span>{secondLabel}</span><select value={second} onChange={(e) => setSecond(e.target.value)}><option value="">Select</option>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select></label></div><button className="primary" disabled={busy || !first || !second} onClick={() => onRun({ first, second })}>{busy ? 'Running...' : 'Run Analysis'}</button></Panel>
}

function RegressionAnalysis({ variables, onRun, busy }: { variables: string[]; onRun: (path: string, config: Record<string, unknown>) => void; busy: boolean }) {
  const [outcome, setOutcome] = useState(''); const [predictors, setPredictors] = useState<string[]>([]); const [categorical, setCategorical] = useState<string[]>([]); const [model, setModel] = useState<'poisson' | 'logistic'>('poisson')
  return <Panel title="Regression"><div className="two-col"><label className="field"><span>Model</span><select value={model} onChange={(e) => setModel(e.target.value as 'poisson' | 'logistic')}><option value="poisson">Robust Poisson — Risk Ratio</option><option value="logistic">Logistic — Odds Ratio</option></select></label><label className="field"><span>Binary outcome</span><select value={outcome} onChange={(e) => setOutcome(e.target.value)}><option value="">Select</option>{variables.map((v) => <option key={v} value={v}>{v}</option>)}</select></label></div><label className="field"><span>Predictors</span><select multiple value={predictors} onChange={(e) => setPredictors(Array.from(e.target.selectedOptions).map((o) => o.value))}>{variables.filter((v) => v !== outcome).map((v) => <option key={v} value={v}>{v}</option>)}</select></label><label className="field"><span>Categorical predictors</span><select multiple value={categorical} onChange={(e) => setCategorical(Array.from(e.target.selectedOptions).map((o) => o.value))}>{predictors.map((v) => <option key={v} value={v}>{v}</option>)}</select></label><button className="primary" disabled={busy || !outcome || predictors.length === 0} onClick={() => onRun(model === 'poisson' ? '/api/v1/analysis/poisson' : '/api/v1/analysis/logistic', { outcome, predictors, categorical_predictors: categorical, reference_categories: {} })}>{busy ? 'Running...' : `Run ${model === 'poisson' ? 'RR' : 'OR'} Model`}</button></Panel>
}

function Results({ result }: { result: unknown }) {
  function download() { const blob = new Blob([JSON.stringify(result ?? {}, null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'medical-analysis-results.json'; a.click(); URL.revokeObjectURL(url) }
  return <Panel title="Results & Export"><div className="result-actions"><button className="secondary" onClick={download} disabled={!result}>Download JSON</button></div><pre className="result">{result ? JSON.stringify(result, null, 2) : 'No analysis run yet.'}</pre></Panel>
}
function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <div className="panel"><h2>{title}</h2>{children}</div> }
function Empty({ text }: { text: string }) { return <div className="empty"><b>No data yet</b><span>{text}</span></div> }

createRoot(document.getElementById('root')!).render(<App />)
