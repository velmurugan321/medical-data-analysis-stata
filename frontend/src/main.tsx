import { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  LayoutDashboard, Upload as UploadIcon, Table2, ShieldCheck, Sigma,
  TableProperties, Link2, TrendingUp, Stethoscope, Activity, PieChart,
  FileDown, Menu, X, ArrowRight, Check, ChevronRight, CircleAlert,
  FileSpreadsheet, Database, Hash, Columns3, Cpu, Loader2, Sparkles,
} from 'lucide-react'
import { DatasetCharts, RocChart } from './charts'
import './styles.css'

type Module = 'dashboard'|'upload'|'variables'|'quality'|'descriptive'|'table1'|'association'|'regression'|'diagnostic'|'roc'|'graphs'|'results'
type Info = { filename?: string; rows:number; columns:number; variables:Array<Record<string,unknown>> }
type ApiResponse = Record<string, any>
type IconType = typeof LayoutDashboard

const API = 'https://medical-data-analysis-api.onrender.com'

const modules: [Module, string, IconType][] = [
  ['dashboard', 'Dashboard', LayoutDashboard],
  ['upload', 'Data Upload', UploadIcon],
  ['variables', 'Variable View', Table2],
  ['quality', 'Data Quality', ShieldCheck],
  ['descriptive', 'Descriptive', Sigma],
  ['table1', 'Table 1', TableProperties],
  ['association', 'Association', Link2],
  ['regression', 'Regression', TrendingUp],
  ['diagnostic', 'Diagnostic', Stethoscope],
  ['roc', 'ROC Analysis', Activity],
  ['graphs', 'Graphs', PieChart],
  ['results', 'Results & Export', FileDown],
]

function App() {
  const [active, setActive] = useState<Module>('dashboard')
  const [file, setFile] = useState<File | null>(null)
  const [info, setInfo] = useState<Info | null>(null)
  const [quality, setQuality] = useState<any>(null)
  const [result, setResult] = useState<ApiResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('Upload a dataset to begin')
  const [apiStatus, setApiStatus] = useState<'ok' | 'error' | 'checking'>('checking')
  const [navOpen, setNavOpen] = useState(false)

  useEffect(() => {
    fetch(`${API}/health`).then(r => { if (!r.ok) throw Error(); setApiStatus('ok') }).catch(() => setApiStatus('error'))
  }, [])

  const variables = useMemo(() => info?.variables.map(v => String(v.name)) || [], [info])

  async function post(path: string, fields: Record<string, string> = {}) {
    if (!file) throw Error('Please upload a dataset first.')
    const f = new FormData()
    f.append('file', file)
    Object.entries(fields).forEach(([k, v]) => f.append(k, v))
    const r = await fetch(`${API}${path}`, { method: 'POST', body: f })
    const text = await r.text()
    if (!r.ok) throw Error(text || `Request failed (${r.status})`)
    return JSON.parse(text)
  }

  async function loadDataset(next: File) {
    setFile(next); setBusy(true); setMessage('Reading dataset and checking quality…')
    try {
      const f = new FormData(); f.append('file', next)
      const r = await fetch(`${API}/api/v1/data/inspect`, { method: 'POST', body: f })
      if (!r.ok) throw Error(await r.text())
      const i = await r.json(); setInfo(i)
      const qf = new FormData(); qf.append('file', next)
      const q = await fetch(`${API}/api/v1/data/quality`, { method: 'POST', body: qf })
      setQuality(q.ok ? (await q.json()).results : null)
      setResult(null); setMessage('Dataset is ready for analysis'); setActive('dashboard')
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Upload failed')
    } finally { setBusy(false) }
  }

  async function run(path: string, fields: Record<string, string>) {
    setBusy(true); setMessage('Running analysis…')
    try {
      setResult(await post(path, fields)); setActive('results'); setMessage('Analysis completed successfully')
    } catch (e) {
      setResult({ error: e instanceof Error ? e.message : 'Analysis failed' })
      setActive('results'); setMessage('Analysis failed — review the message below')
    } finally { setBusy(false) }
  }

  const go = (m: Module) => { setActive(m); setNavOpen(false) }
  const activeMeta = modules.find(x => x[0] === active)

  return (
    <div className={`app ${navOpen ? 'nav-open' : ''}`}>
      <div className="scrim" onClick={() => setNavOpen(false)} />
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Sparkles size={18} /></div>
          <div><strong>Medical Analytics</strong><span>Research statistics platform</span></div>
          <button className="nav-close" onClick={() => setNavOpen(false)} aria-label="Close menu"><X size={18} /></button>
        </div>
        <div className="side-section">Workspace</div>
        <nav>
          {modules.map(([id, label, Icon]) => (
            <button key={id} className={active === id ? 'active' : ''} onClick={() => go(id)}>
              <Icon size={17} strokeWidth={2} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="side-footer">
          <span className={`dot ${apiStatus === 'error' ? 'bad' : apiStatus === 'checking' ? 'warn' : ''}`} />
          {apiStatus === 'ok' ? 'Analysis engine online' : apiStatus === 'error' ? 'Analysis engine offline' : 'Connecting…'}
          <small>Python statistical engine</small>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <button className="hamburger" onClick={() => setNavOpen(true)} aria-label="Open menu"><Menu size={20} /></button>
          <div className="topbar-brand"><div className="brand-mark sm"><Sparkles size={14} /></div>Medical Analytics</div>
          <label className="top-upload sm"><UploadIcon size={15} /><span>Upload</span>
            <input hidden type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={e => e.target.files?.[0] && loadDataset(e.target.files[0])} />
          </label>
        </div>

        <header>
          <div>
            <span className="eyebrow">Clinical research workspace</span>
            <h1>{activeMeta?.[1]}</h1>
            <p>{file ? `${file.name}  ·  ${info?.rows ?? '—'} records  ·  ${info?.columns ?? '—'} variables` : 'A clean workflow for medical data analysis'}</p>
          </div>
          <label className="top-upload">
            <UploadIcon size={16} /><span>Upload dataset</span>
            <input hidden type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={e => e.target.files?.[0] && loadDataset(e.target.files[0])} />
          </label>
        </header>

        <div className={`statusbar ${apiStatus}`}>
          {busy ? <Loader2 size={15} className="spin" /> : <span className="status-dot" />}
          <b>{apiStatus === 'ok' ? 'Engine ready' : apiStatus === 'error' ? 'Engine unavailable' : 'Checking engine'}</b>
          <span>{message}</span>
        </div>

        {active === 'dashboard' && <Dashboard info={info} apiStatus={apiStatus} onUpload={() => go('upload')} onRun={() => go('descriptive')} onModule={go} />}
        {active === 'upload' && <Upload file={file} busy={busy} onUpload={loadDataset} />}
        {active === 'variables' && <Panel title="Variable View" subtitle="Understand every variable before selecting an analysis.">
          {info ? <VariableTable variables={info.variables} /> : <Empty icon={Columns3} title="No dataset loaded" text="Upload a CSV, Excel, Stata or TSV file to inspect variables." />}
        </Panel>}
        {active === 'quality' && <Quality data={quality} />}
        {active === 'descriptive' && <VariablePicker title="Descriptive Statistics" variables={variables} hint="Choose one or more variables. Nothing is selected by default, so the analysis only runs on variables you explicitly choose." action="Run descriptive analysis" busy={busy} onRun={v => v.length ? run('/api/v1/analysis/descriptive', { variables: v.join(',') }) : setMessage('Select at least one variable before running the analysis')} />}
        {active === 'table1' && <TableOne variables={variables} busy={busy} onRun={v => v.variables.length ? run('/api/v1/analysis/table-one', { variables: v.variables.join(','), group: v.group }) : setMessage('Select at least one variable for Table 1')} />}
        {active === 'association' && <PairAnalysis title="Categorical Association" subtitle="Compare two categorical variables using chi-square / Fisher exact." a="Exposure / variable" b="Outcome" variables={variables} busy={busy} onRun={v => run('/api/v1/analysis/association', { variable: v.a, outcome: v.b })} />}
        {active === 'diagnostic' && <PairAnalysis title="Diagnostic Accuracy" subtitle="Compare an index test against the reference standard." a="Index test" b="Reference standard" variables={variables} busy={busy} onRun={v => run('/api/v1/analysis/diagnostic', { index_test: v.a, reference_standard: v.b })} />}
        {active === 'roc' && <PairAnalysis title="ROC Analysis" subtitle="Evaluate discrimination and identify the Youden-optimal threshold." a="Test / predictor" b="Binary outcome" variables={variables} busy={busy} onRun={v => run('/api/v1/analysis/roc', { test: v.a, outcome: v.b })} />}
        {active === 'regression' && <Regression variables={variables} busy={busy} onRun={(path, c) => run(path, { config: JSON.stringify(c) })} />}
        {active === 'graphs' && <Panel title="Publication-ready graphs" subtitle="Visual summaries generated from your loaded dataset.">
          {info ? <DatasetCharts variables={info.variables} /> : <Empty icon={PieChart} title="No dataset loaded" text="Upload a dataset to generate charts of missingness, variable types and completeness." />}
        </Panel>}
        {active === 'results' && <Results result={result} />}
      </main>
    </div>
  )
}

function Dashboard({ info, apiStatus, onUpload, onRun, onModule }: { info: Info | null; apiStatus: string; onUpload: () => void; onRun: () => void; onModule: (m: Module) => void }) {
  const cards: [Module, string, string, IconType][] = [
    ['quality', 'Data Quality', 'Missing data, duplicates & consistency', ShieldCheck],
    ['descriptive', 'Descriptive', 'Mean, SD, median & distributions', Sigma],
    ['table1', 'Table 1', 'Publication-style baseline table', TableProperties],
    ['association', 'Association', 'Chi-square & Fisher exact', Link2],
    ['regression', 'Regression', 'RR and OR models', TrendingUp],
    ['diagnostic', 'Diagnostic', 'Sensitivity, specificity & CI', Stethoscope],
  ]
  return (
    <div className="dashboard">
      <section className="hero">
        <div className="hero-copy">
          <div className="hero-badge"><span />Medical data analysis</div>
          <h2>From raw dataset to <em>research-ready</em> results.</h2>
          <p>Upload your clinical data, inspect variables, choose an analysis visually, and get clean statistical tables — without writing a single line of statistical code.</p>
          <div className="hero-actions">
            <button className="primary" onClick={onUpload}>Upload dataset <ArrowRight size={16} /></button>
            {info && <button className="ghost" onClick={onRun}>Start analysis</button>}
          </div>
          <div className="trust-row">
            {['CSV', 'Excel', 'Stata', 'TSV'].map(t => <span key={t}><Check size={13} />{t}</span>)}
          </div>
        </div>
        <div className="hero-visual">
          <div className="visual-window">
            <div className="window-top"><span /><span /><span /><b>Analysis workspace</b></div>
            <div className="mini-chart">
              <div className="chart-bars">{[42, 68, 54, 86, 63].map((h, i) => <i key={i} style={{ height: `${h}%` }} />)}</div>
              <div className="chart-line"><span>RR</span><b>1.42</b><small>95% CI 1.08–1.87</small></div>
            </div>
            <div className="mini-table">{Array.from({ length: 6 }).map((_, i) => <span key={i} />)}</div>
          </div>
        </div>
      </section>

      <div className="stat-grid">
        <Stat icon={FileSpreadsheet} label="Dataset" value={info?.filename || 'Not loaded'} />
        <Stat icon={Hash} label="Records" value={info ? info.rows.toLocaleString() : '—'} />
        <Stat icon={Columns3} label="Variables" value={info ? String(info.columns) : '—'} />
        <Stat icon={Cpu} label="Engine" value={apiStatus === 'ok' ? 'Online' : apiStatus === 'error' ? 'Offline' : 'Checking'} tone={apiStatus === 'ok' ? 'good' : apiStatus === 'error' ? 'bad' : ''} />
      </div>

      <section className="section-block">
        <div className="section-heading">
          <div><span className="eyebrow">Workflow</span><h3>Everything you need in one workspace</h3></div>
          <span className="section-note">Built for medical research</span>
        </div>
        <div className="module-grid">
          {cards.map(([id, t, d, Icon]) => (
            <button className="module-card" key={id} onClick={() => onModule(id)}>
              <span className="module-icon"><Icon size={20} /></span>
              <div><b>{t}</b><small>{d}</small></div>
              <ChevronRight size={18} className="module-arrow" />
            </button>
          ))}
        </div>
      </section>

      <section className="bottom-callout">
        <div>
          <span className="eyebrow">Simple by design</span>
          <h3>Select → Run → Review</h3>
          <p>No statistical syntax required. Your data stays in the analysis workflow while results are presented as readable research output.</p>
        </div>
        <button className="secondary" onClick={onUpload}>Begin with a dataset</button>
      </section>
    </div>
  )
}

function Stat({ icon: Icon, label, value, tone = '' }: { icon: IconType; label: string; value: string | number; tone?: string }) {
  return (
    <div className="stat-card">
      <span className={`stat-icon ${tone}`}><Icon size={18} /></span>
      <div><small>{label}</small><b title={String(value)}>{value}</b></div>
    </div>
  )
}

function Upload({ file, busy, onUpload }: { file: File | null; busy: boolean; onUpload: (f: File) => void }) {
  const [drag, setDrag] = useState(false)
  return (
    <Panel title="Upload Dataset" subtitle="Supported: CSV, XLSX, XLS, Stata DTA and TSV.">
      <label
        className={`drop ${drag ? 'drag' : ''} ${busy ? 'busy' : ''}`}
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); e.dataTransfer.files?.[0] && onUpload(e.dataTransfer.files[0]) }}
      >
        <div className="drop-icon">{busy ? <Loader2 size={26} className="spin" /> : <UploadIcon size={26} />}</div>
        <b>{busy ? 'Processing dataset…' : 'Drop your dataset here'}</b>
        <span>or click to browse files</span>
        <input type="file" accept=".csv,.xlsx,.xls,.dta,.tsv" onChange={e => e.target.files?.[0] && onUpload(e.target.files[0])} />
      </label>
      {file && (
        <div className="file-row">
          <span className="file-icon"><Check size={16} /></span>
          <div><b>{file.name}</b><small>Dataset loaded and ready</small></div>
          <em>{(file.size / 1024).toFixed(1)} KB</em>
        </div>
      )}
    </Panel>
  )
}

function VariableTable({ variables }: { variables: Array<Record<string, unknown>> }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{['Variable', 'Type', 'Storage', 'N', 'Missing', 'Unique', 'Min', 'Max'].map(x => <th key={x}>{x}</th>)}</tr></thead>
        <tbody>
          {variables.map(v => (
            <tr key={String(v.name)}>
              <td><b>{String(v.name)}</b></td>
              <td><span className="type-pill">{String(v.type)}</span></td>
              <td>{String(v.storage_type)}</td>
              <td>{String(v.n)}</td>
              <td>{String(v.missing)}</td>
              <td>{String(v.unique)}</td>
              <td>{v.min == null ? '—' : String(v.min)}</td>
              <td>{v.max == null ? '—' : String(v.max)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function VariablePicker({ title, variables, hint, action, busy, onRun }: { title: string; variables: string[]; hint: string; action: string; busy: boolean; onRun: (v: string[]) => void }) {
  const [selected, setSelected] = useState<string[]>([])
  const all = variables.length > 0 && selected.length === variables.length
  const toggle = (v: string) => setSelected(s => s.includes(v) ? s.filter(x => x !== v) : [...s, v])
  return (
    <Panel title={title} subtitle={hint}>
      <SelectionToolbar count={selected.length} all={all} onAll={() => setSelected(all ? [] : variables)} />
      <div className="variable-grid">
        {variables.map(v => (
          <button type="button" key={v} className={`variable-chip ${selected.includes(v) ? 'selected' : ''}`} onClick={() => toggle(v)}>
            <span className="check">{selected.includes(v) && <Check size={12} />}</span><span>{v}</span>
          </button>
        ))}
      </div>
      {!variables.length && <Empty icon={Columns3} title="No variables available" text="Upload a dataset before selecting variables." />}
      <div className="action-row">
        <button className="primary" disabled={busy || !selected.length} onClick={() => onRun(selected)}>{busy ? 'Running…' : action}<ArrowRight size={16} /></button>
      </div>
    </Panel>
  )
}

function SelectionToolbar({ count, all, onAll }: { count: number; all: boolean; onAll: () => void }) {
  return (
    <div className="selection-toolbar">
      <div><b>{count}</b><span> variable{count === 1 ? '' : 's'} selected</span></div>
      <button className="link" onClick={onAll}>{all ? 'Clear all' : 'Select all'}</button>
    </div>
  )
}

function TableOne({ variables, busy, onRun }: { variables: string[]; busy: boolean; onRun: (v: { variables: string[]; group: string }) => void }) {
  const [selected, setSelected] = useState<string[]>([])
  const [group, setGroup] = useState('')
  const all = variables.length > 0 && selected.length === variables.length
  const toggle = (v: string) => setSelected(s => s.includes(v) ? s.filter(x => x !== v) : [...s, v])
  return (
    <Panel title="Table 1" subtitle="Build a baseline characteristics table with an optional grouping variable.">
      <SelectionToolbar count={selected.length} all={all} onAll={() => setSelected(all ? [] : variables)} />
      <div className="variable-grid">
        {variables.map(v => (
          <button type="button" key={v} className={`variable-chip ${selected.includes(v) ? 'selected' : ''}`} onClick={() => toggle(v)}>
            <span className="check">{selected.includes(v) && <Check size={12} />}</span>{v}
          </button>
        ))}
      </div>
      <label className="field">
        <span>Grouping variable <small>(optional)</small></span>
        <select value={group} onChange={e => setGroup(e.target.value)}>
          <option value="">Overall only</option>
          {variables.map(v => <option key={v}>{v}</option>)}
        </select>
      </label>
      <div className="action-row">
        <button className="primary" disabled={busy || !selected.length} onClick={() => onRun({ variables: selected, group })}>{busy ? 'Generating…' : 'Generate Table 1'}<ArrowRight size={16} /></button>
      </div>
    </Panel>
  )
}

function PairAnalysis({ title, subtitle, a, b, variables, busy, onRun }: { title: string; subtitle: string; a: string; b: string; variables: string[]; busy: boolean; onRun: (v: { a: string; b: string }) => void }) {
  const [x, setX] = useState('')
  const [y, setY] = useState('')
  return (
    <Panel title={title} subtitle={subtitle}>
      {!variables.length
        ? <Empty icon={Columns3} title="No variables available" text="Upload a dataset before running this analysis." />
        : <>
          <div className="selection-grid">
            <SelectBox label={a} value={x} set={setX} variables={variables} />
            <SelectBox label={b} value={y} set={setY} variables={variables} />
          </div>
          {x && y && x === y && <div className="warning"><CircleAlert size={15} />Choose two different variables for this analysis.</div>}
          <div className="action-row">
            <button className="primary" disabled={busy || !x || !y || x === y} onClick={() => onRun({ a: x, b: y })}>{busy ? 'Running…' : 'Run analysis'}<ArrowRight size={16} /></button>
          </div>
        </>}
    </Panel>
  )
}

function SelectBox({ label, value, set, variables }: { label: string; value: string; set: (v: string) => void; variables: string[] }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={e => set(e.target.value)}>
        <option value="">Choose a variable…</option>
        {variables.map(v => <option key={v}>{v}</option>)}
      </select>
    </label>
  )
}

function Regression({ variables, busy, onRun }: { variables: string[]; busy: boolean; onRun: (path: string, c: Record<string, unknown>) => void }) {
  const [model, setModel] = useState('poisson')
  const [outcome, setOutcome] = useState('')
  const [predictors, setPredictors] = useState<string[]>([])
  const [cat, setCat] = useState<string[]>([])
  const [refs, setRefs] = useState<Record<string, string>>({})
  const predictorVars = variables.filter(v => v !== outcome)
  const toggle = (v: string) => setPredictors(s => s.includes(v) ? s.filter(x => x !== v) : [...s, v])
  const toggleCat = (v: string) => setCat(s => s.includes(v) ? s.filter(x => x !== v) : [...s, v])
  const path = model === 'logistic' ? '/api/v1/analysis/regression/logistic' : '/api/v1/analysis/regression/poisson'
  const canRun = !!outcome && predictors.length > 0 && !busy

  if (!variables.length) {
    return <Panel title="Regression" subtitle="Configure the outcome, predictors, categorical variables and reference categories before running the model.">
      <Empty icon={Columns3} title="No variables available" text="Upload a dataset before configuring a regression model." />
    </Panel>
  }

  return (
    <Panel title="Regression" subtitle="Configure the outcome, predictors, categorical variables and reference categories before running the model.">
      <div className="selection-grid">
        <SelectBox label="Outcome (binary 0/1)" value={outcome} set={v => { setOutcome(v); setPredictors(p => p.filter(x => x !== v)); setCat(c => c.filter(x => x !== v)) }} variables={variables} />
        <label className="field">
          <span>Model</span>
          <select value={model} onChange={e => setModel(e.target.value)}>
            <option value="poisson">Robust Poisson — Risk Ratio</option>
            <option value="logistic">Logistic — Odds Ratio</option>
          </select>
        </label>
      </div>
      <div className="selection-block">
        <div className="block-title"><b>Predictors</b><span>Select the independent variables for the model.</span></div>
        <SelectionToolbar count={predictors.length} all={predictorVars.length > 0 && predictors.length === predictorVars.length} onAll={() => setPredictors(predictors.length === predictorVars.length ? [] : predictorVars)} />
        <div className="variable-grid compact">
          {predictorVars.map(v => (
            <button type="button" key={v} className={`variable-chip ${predictors.includes(v) ? 'selected' : ''}`} onClick={() => toggle(v)}>
              <span className="check">{predictors.includes(v) && <Check size={12} />}</span>{v}
            </button>
          ))}
        </div>
      </div>
      {predictors.length > 0 && (
        <div className="selection-block">
          <div className="block-title"><b>Categorical predictors</b><span>Select only variables that represent categories.</span></div>
          <div className="variable-grid compact">
            {predictors.map(v => (
              <button type="button" key={v} className={`variable-chip ${cat.includes(v) ? 'selected' : ''}`} onClick={() => toggleCat(v)}>
                <span className="check">{cat.includes(v) && <Check size={12} />}</span>{v}
              </button>
            ))}
          </div>
        </div>
      )}
      {cat.length > 0 && (
        <div className="selection-block">
          <div className="block-title"><b>Reference categories</b><span>Optionally set the baseline level for each categorical variable.</span></div>
          <div className="ref-grid">
            {cat.map(v => (
              <label className="field" key={v}>
                <span>{v}</span>
                <input value={refs[v] || ''} placeholder="e.g. 0" onChange={e => setRefs(r => ({ ...r, [v]: e.target.value }))} />
              </label>
            ))}
          </div>
        </div>
      )}
      <div className="action-row">
        <button className="primary" disabled={!canRun} onClick={() => onRun(path, { outcome, predictors, categorical: cat, reference: refs, model })}>{busy ? 'Fitting model…' : 'Run regression'}<ArrowRight size={16} /></button>
      </div>
    </Panel>
  )
}

function Quality({ data }: { data: any }) {
  if (!data) return (
    <Panel title="Data Quality" subtitle="Automatic checks for missingness, duplicates and variable issues.">
      <Empty icon={ShieldCheck} title="No dataset loaded" text="Upload a dataset to start quality checks." />
    </Panel>
  )
  const numeric = Object.entries(data).filter(([, v]) => typeof v === 'number')
  return (
    <Panel title="Data Quality" subtitle="Automatic checks completed when the dataset was uploaded.">
      <div className="quality-cards">
        {numeric.slice(0, 6).map(([k, v]) => <Stat key={k} icon={ShieldCheck} label={pretty(k)} value={String(v)} />)}
      </div>
      <HumanResult data={data} />
    </Panel>
  )
}

function extractRocPoints(data: any): Array<{ fpr: number; tpr: number }> | null {
  const search = (obj: any): any[] | null => {
    if (!obj || typeof obj !== 'object') return null
    for (const [k, v] of Object.entries(obj)) {
      if (Array.isArray(v) && v.length && typeof v[0] === 'object' && v[0]) {
        const keys = Object.keys(v[0]).map(x => x.toLowerCase())
        const hasFpr = keys.some(x => x.includes('fpr') || x.includes('1-spec') || x === 'x')
        const hasTpr = keys.some(x => x.includes('tpr') || x.includes('sens') || x === 'y')
        if ((hasFpr && hasTpr) || (/roc|curve/i.test(k) && keys.length >= 2)) return v
      }
      if (v && typeof v === 'object') { const found = search(v); if (found) return found }
    }
    return null
  }
  const arr = search(data)
  if (!arr) return null
  const pick = (o: any, names: string[]) => {
    for (const key of Object.keys(o)) { const lk = key.toLowerCase(); if (names.some(n => lk.includes(n))) return Number(o[key]) }
    return NaN
  }
  const points = arr.map(o => ({
    fpr: pick(o, ['fpr', '1-spec', 'x']),
    tpr: pick(o, ['tpr', 'sens', 'y']),
  })).filter(p => Number.isFinite(p.fpr) && Number.isFinite(p.tpr))
  return points.length > 2 ? points.sort((a, b) => a.fpr - b.fpr) : null
}

function Results({ result }: { result: ApiResponse | null }) {
  const roc = result && !result.error ? extractRocPoints(result) : null
  return (
    <Panel title="Analysis Results" subtitle="Readable research output. Raw data is available as CSV or JSON download.">
      <div className="result-toolbar">
        <span className={result?.error ? 'warn-text' : ''}>{result?.error ? 'Analysis needs attention' : result ? 'Results ready for review' : 'No results yet'}</span>
        <div className="toolbar-actions">
          <button className="secondary" disabled={!result || !!result.error} onClick={() => downloadCSV(result)}>Download CSV</button>
          <button className="secondary" disabled={!result} onClick={() => downloadJSON(result)}><FileDown size={15} />JSON</button>
        </div>
      </div>
      {result ? <>
        {roc && <RocChart points={roc} />}
        <HumanResult data={result} />
      </> : <Empty icon={FileDown} title="No results yet" text="Run an analysis to generate results here." />}
    </Panel>
  )
}

function HumanResult({ data }: { data: any }) {
  if (data?.error) return <div className="error-box"><CircleAlert size={18} /><span>{String(data.error)}</span></div>
  const payload = data?.results ?? data
  if (Array.isArray(payload)) return <SimpleTable rows={payload} />
  if (payload && typeof payload === 'object') {
    const entries = Object.entries(payload)
    const scalar = entries.filter(([, v]) => v == null || ['string', 'number', 'boolean'].includes(typeof v))
    return <>
      {scalar.length > 0 && <div className="metric-list">{scalar.map(([k, v]) => <div className="metric" key={k}><span>{pretty(k)}</span><b>{format(v)}</b></div>)}</div>}
      <ComplexTables data={payload} />
    </>
  }
  return <div className="metric-list"><div className="metric"><span>Result</span><b>{format(payload)}</b></div></div>
}

function ComplexTables({ data }: { data: any }) {
  return <>{Object.entries(data || {}).filter(([, v]) => Array.isArray(v) && v.length && typeof (v as any[])[0] === 'object').map(([k, v]) => (
    <div className="result-table" key={k}><h3>{pretty(k)}</h3><SimpleTable rows={v as any[]} /></div>
  ))}</>
}

function SimpleTable({ rows }: { rows: any[] }) {
  if (!rows.length) return null
  const keys = Array.from(new Set(rows.flatMap(r => typeof r === 'object' && r ? Object.keys(r) : ['value'])))
  return (
    <div className="table-wrap">
      <table>
        <thead><tr>{keys.map(k => <th key={k}>{pretty(k)}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{keys.map(k => <td key={k}>{format(r?.[k])}</td>)}</tr>)}</tbody>
      </table>
    </div>
  )
}

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: any }) {
  return (
    <section className="panel">
      <div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div></div>
      {children}
    </section>
  )
}

function Empty({ icon: Icon, title, text }: { icon: IconType; title: string; text: string }) {
  return <div className="empty"><div className="empty-icon"><Icon size={26} /></div><b>{title}</b><span>{text}</span></div>
}

function pretty(k: string) { return k.replaceAll('_', ' ').replace(/\b\w/g, m => m.toUpperCase()) }

function format(v: any): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') {
    if (!Number.isFinite(v)) return 'Not estimable'
    return Math.abs(v) < 0.001 && v !== 0 ? v.toExponential(2) : Number.isInteger(v) ? String(v) : v.toFixed(3)
  }
  if (typeof v === 'boolean') return v ? 'Yes' : 'No'
  if (Array.isArray(v)) return v.map(format).join(', ')
  if (typeof v === 'object') return Object.entries(v).map(([k, x]) => `${pretty(k)}: ${format(x)}`).join(' · ')
  return String(v)
}

function firstTable(data: any): any[] | null {
  const payload = data?.results ?? data
  if (Array.isArray(payload) && payload.length && typeof payload[0] === 'object') return payload
  if (payload && typeof payload === 'object') {
    for (const v of Object.values(payload)) {
      if (Array.isArray(v) && v.length && typeof v[0] === 'object') return v as any[]
    }
  }
  return null
}

function downloadCSV(data: any) {
  const rows = firstTable(data)
  if (!rows) { downloadJSON(data); return }
  const keys = Array.from(new Set(rows.flatMap(r => Object.keys(r))))
  const esc = (v: any) => { const s = v == null ? '' : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s }
  const csv = [keys.join(','), ...rows.map(r => keys.map(k => esc(r[k])).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'medical-analysis-results.csv'; a.click(); URL.revokeObjectURL(a.href)
}

function downloadJSON(data: any) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'medical-analysis-results.json'; a.click(); URL.revokeObjectURL(a.href)
}

createRoot(document.getElementById('root')!).render(<App />)
