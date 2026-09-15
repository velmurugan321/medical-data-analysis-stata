import { useMemo, useState } from 'react'

type Profile = Record<string, any>
type Workbook = { filename:string; sheet_count:number; sheets:Array<{sheet:string;status:string;rows?:number;columns?:number;variables?:Profile[]}> }

const API='https://medical-data-analysis-api.onrender.com'

export function VariableIntelligence({files,onComplete}:{files:File[];onComplete:(contract:any[])=>void}){
 const [data,setData]=useState<{files:Workbook[]}|null>(null)
 const [busy,setBusy]=useState(false)
 const [review,setReview]=useState<Record<string,string>>({})
 const [error,setError]=useState('')
 const [open,setOpen]=useState(false)
 const profiles=useMemo(()=>data?.files.flatMap(f=>f.sheets.flatMap(s=>(s.variables||[]).map(v=>({...v,file:f.filename,sheet:s.sheet}))))||[],[data])
 const needs=(v:Profile)=>v.detected_type==='binary/code'||v.detected_type==='categorical/code'||!!v.warnings?.length||v.confidence<.9
 const suggested=(v:Profile)=>v.detected_type==='numeric'?'numeric':v.detected_type==='binary/code'?'binary':v.detected_type.includes('categorical')?'categorical':v.detected_type==='date/time'?'date/time':v.detected_type==='identifier'?'identifier':'text'
 async function inspect(){
  if(!files.length)return
  setBusy(true);setError('')
  try{const fd=new FormData();files.forEach(f=>fd.append('files',f));const r=await fetch(`${API}/api/v1/data/inspect-workbooks`,{method:'POST',body:fd});if(!r.ok)throw Error(await r.text());const d=await r.json();setData(d);const initial:Record<string,string>={};d.files.forEach((f:Workbook)=>f.sheets.forEach(s=>(s.variables||[]).forEach(v=>{const k=`${f.filename}|${s.sheet}|${v.name}`;if(!needs(v))initial[k]=suggested(v)})));setReview(initial);setOpen(true)}catch(e){setError(e instanceof Error?e.message:'Inspection failed')}finally{setBusy(false)}
 }
 function proceed(){const missing=profiles.filter(v=>!review[`${v.file}|${v.sheet}|${v.name}`]);if(missing.length){setError(`${missing.length} variable(s) still need confirmation.`);return}const contract=profiles.map(v=>({...v,confirmed_type:review[`${v.file}|${v.sheet}|${v.name}`],coding:{}}));onComplete(contract)}
 if(!open)return <div className="panel-inline"><div><b>Variable Intelligence</b><small>Inspect every workbook sheet before statistical analysis.</small></div><button className="secondary" disabled={!files.length||busy} onClick={inspect}>{busy?'Inspecting…':'Inspect variables'}</button>{error&&<div className="warning">{error}</div>}</div>
 return <div className="variable-intelligence"><div className="review-head"><div><b>Variable Intelligence Review</b><small>{profiles.length} variables detected · ambiguous variables require confirmation</small></div><button className="primary" onClick={proceed}>Proceed to analysis →</button></div>{error&&<div className="warning">{error}</div>}<div className="table-wrap"><table><thead><tr><th>File / Sheet</th><th>Variable</th><th>Detected</th><th>N</th><th>Missing</th><th>Unique</th><th>Confidence</th><th>Confirm type</th><th>Warnings</th></tr></thead><tbody>{profiles.map(v=>{const k=`${v.file}|${v.sheet}|${v.name}`;const required=needs(v);return <tr key={k}><td>{v.file}<br/><small>{v.sheet}</small></td><td><b>{v.name}</b></td><td>{v.detected_type}</td><td>{v.n}</td><td>{v.missing} ({v.missing_percent}%)</td><td>{v.unique}</td><td>{v.confidence_percent}%</td><td>{required?<select value={review[k]||''} onChange={e=>setReview(x=>({...x,[k]:e.target.value}))}><option value="">Select…</option><option value="numeric">Continuous numeric</option><option value="binary">Binary categorical</option><option value="categorical">Categorical / ordinal</option><option value="date/time">Date / time</option><option value="identifier">Identifier</option><option value="text">Text</option></select>:<span>✓ {review[k]}</span>}</td><td>{v.warnings?.length?<span className="warning">{v.warnings.join('; ')}</span>:'—'}</td></tr>})}</tbody></table></div><p className="muted">Safety rule: detection never silently recodes the raw dataset. Numeric codes such as 1/2/3 and short codes such as M/F or Y/N remain reviewable.</p></div>
}
