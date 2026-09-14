import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Module = 'dashboard' | 'upload' | 'variables' | 'quality' | 'descriptive' | 'association' | 'regression' | 'diagnostic' | 'roc' | 'graphs' | 'results'
type Info = { rows: number; columns: number; variables: Array<Record<string, unknown>> }

const modules: Array<{ id: Module; label: string; icon: string }> = [
  { id: 'dashboard', label: 'Dashboard', icon: '▦' },
  { id: 'upload', label: 'Data Upload', icon: '⇧' },
  { id: 'variables', label: 'Variable View', icon: '☷' },
  { id: 'quality', label: 'Data Quality', icon: '✓' },
  { id: 'descriptive', label: 'Descriptive', icon: '▤' },
  { id: 'association', label: 'Association', icon: '↔' },
  { id: 'regression', label: 'Regression', icon: 'β' },
  { id: 'diagnostic', label: 'Diagnostic', icon: '⊞' },
  { id: 'roc', label: 'ROC Analysis', icon: '⌁' },
  { id: 'graphs', label: 'Graphs', icon: '◒' },
  { id: 'results', label: 'Results & Export', icon: '⇩' }
]

const API = (window as Window & { MEDICAL_ANALYTICS_API?: string }).MEDICAL_ANALYTICS_API || window.location.origin

function App() {
  const [active, setActive] = useState<Module>('dashboard')
  const [file, setFile] = useState<File | null>(null)
  const [info, setInfo] = useState<Info | null>(null)
  const [quality, setQuality] = useState<unknown>(null)
  const [result, setResult] = useState<unknown>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('No dataset loaded')

  async function post(path: string, fields: Record<string, string> = {}) {
    if (!file) throw new Error('Upload a dataset first.')
    const form = new FormData()
    form.append('file', file)
    Object.entries(fields).forEach(([key, value]) => form.append(key, value))
    const response = await fetch(`${API}${path}`, { method: 'POST', body: form })
    const text = await response.text()
    if (!response.ok) throw new Error(text)
    return JSON.parse(text)
  }

  async function loadDataset(next: File) {
    setFile(next)
    setBusy(true)
    setMessage('Inspecting dataset...')
    try {
      const inspected = await post('/api/v1/data/inspect')
      setInfo(inspected)
      const checked = await post('/api/v1/data/quality')
      setQuality(checked.results)
      setMessage('Dataset loaded and quality checked')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'API error')
    } finally {
      setBusy(false)
    }
  }

  async function runAnalysis(path: string, fields: Record<string, string>) {
    setBusy(true)
    try {
      setResult(await post(path, fields))
      setActive('results')
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : 'Analysis failed' })
    } finally {
      setBusy(false)
    }
  }

  const title = modules.find((item) => item.id === active)?.label || 'Dashboard'

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">M</div><div><strong>Medical Analytics Lab</strong><span>Clinical statistics platform</span></div></div>
        <nav>{modules.map((item) => <button key={item.id} className={active === item.id ? 'active' : ''} onClick={() => setActive(item.id)}><i>{item.icon}</i>{item.label}</button>)}</nav>
        <div className="side-footer"><span className="dot" /> Statistical engine connected</div>
      </aside>
      <main className="main">
        <header><div><span className="eyebrow">Medical statistics</span><h1>{title}</h1><p>Upload data, inspect variables, run validated clinical analyses and export results.</p></div><label className="primary">+ Upload Dataset<input hidden type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={(event) => event.target.files?.[0] && loadDataset(event.target.files[0])} /></label></header>
        {active === 'dashboard' && <Dashboard info={info} message={message} busy={busy} onUpload={() => setActive('upload')} />}
        {active === 'upload' && <Upload file={file} busy={busy} message={message} onUpload={loadDataset} />}
        {active === 'variables' && <Panel title="Variable View">{info ? <pre className="result">{JSON.stringify(info.variables, null, 2)}</pre> : <Empty text="Upload a dataset to inspect variables." />}</Panel>}
        {active === 'quality' && <Panel title="Data Quality">{quality ? <pre className="result">{JSON.stringify(quality, null, 2)}</pre> : <Empty text="Upload a dataset to run quality checks." />}</Panel>}
        {active === 'descriptive' && <Analysis title="Descriptive Analysis" fields="variables" onRun={(v) => runAnalysis('/api/v1/analysis/descriptive', { variables: v })} busy={busy} />}
        {active === 'association' && <Analysis title="Categorical Association" fields="variable,outcome" onRun={(v) => runAnalysis('/api/v1/analysis/association', { variable: v.split(',')[0] || '', outcome: v.split(',')[1] || '' })} busy={busy} />}
        {active === 'diagnostic' && <Analysis title="Diagnostic Accuracy" fields="index_test,reference_standard" onRun={(v) => runAnalysis('/api/v1/analysis/diagnostic', { index_test: v.split(',')[0] || '', reference_standard: v.split(',')[1] || '' })} busy={busy} />}
        {active === 'roc' && <Analysis title="ROC Analysis" fields="test,outcome" onRun={(v) => runAnalysis('/api/v1/analysis/roc', { test: v.split(',')[0] || '', outcome: v.split(',')[1] || '' })} busy={busy} />}
        {active === 'regression' && <Analysis title="Robust Poisson Regression" fields="JSON model configuration" onRun={(v) => runAnalysis('/api/v1/analysis/poisson', { config: v })} busy={busy} />}
        {active === 'graphs' && <Panel title="Graphs"><Empty text="Validated visualization modules will be connected here." /></Panel>}
        {active === 'results' && <Panel title="Results & Export"><pre className="result">{result ? JSON.stringify(result, null, 2) : 'No analysis run yet.'}</pre></Panel>}
      </main>
    </div>
  )
}

function Dashboard({ info, message, busy, onUpload }: { info: Info | null; message: string; busy: boolean; onUpload: () => void }) {
  return <><div className="hero-grid"><div className="hero"><span className="badge">{busy ? 'PROCESSING' : 'READY'}</span><h2>Clinical analysis, built for reproducibility.</h2><p>From raw dataset to publication-ready statistical results.</p><button className="primary" onClick={onUpload}>Upload your dataset</button></div><div className="pipeline"><span>WORKFLOW</span><div>Upload → Inspect → Quality → Analyze → Validate → Export</div><small>{message}</small></div></div><div className="cards"><Card label="Dataset" value={info ? 'Loaded' : '—'} /><Card label="Rows" value={info ? String(info.rows) : '—'} /><Card label="Variables" value={info ? String(info.columns) : '—'} /><Card label="API" value="Connected" /></div></>
}

function Card({ label, value }: { label: string; value: string }) { return <div className="card"><span>{label}</span><strong>{value}</strong></div> }
function Upload({ file, busy, message, onUpload }: { file: File | null; busy: boolean; message: string; onUpload: (file: File) => void }) { return <Panel title="Upload Dataset"><label className="drop"><b>{busy ? 'Inspecting...' : 'Choose your dataset'}</b><span>CSV, XLSX, XLS, Stata DTA or TSV</span><input type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])} /></label>{file && <div className="file-row"><b>{file.name}</b><em>{message}</em></div>}</Panel> }
function Analysis({ title, fields, onRun, busy }: { title: string; fields: string; onRun: (value: string) => void; busy: boolean }) { const [value, setValue] = useState(''); return <Panel title={title}><p className="muted">Enter {fields}.</p><textarea value={value} onChange={(event) => setValue(event.target.value)} placeholder={fields} /><button className="primary" disabled={busy} onClick={() => onRun(value)}>{busy ? 'Running...' : 'Run Analysis'}</button></Panel> }
function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <div className="panel"><h2>{title}</h2>{children}</div> }
function Empty({ text }: { text: string }) { return <div className="empty"><b>No data yet</b><span>{text}</span></div> }

createRoot(document.getElementById('root')!).render(<App />)
