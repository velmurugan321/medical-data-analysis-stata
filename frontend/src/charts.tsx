import { useMemo } from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts'

type Variable = Record<string, unknown>

const PALETTE = ['#0d9488', '#2563eb', '#7c3aed', '#f59e0b', '#e11d48', '#0891b2', '#65a30d', '#db2777']

function num(v: unknown): number {
  const n = typeof v === 'number' ? v : parseFloat(String(v))
  return Number.isFinite(n) ? n : 0
}

function ChartCard({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="chart-card">
      <div className="chart-card-head">
        <b>{title}</b>
        {hint && <small>{hint}</small>}
      </div>
      <div className="chart-card-body">{children}</div>
    </div>
  )
}

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <span className="chart-tooltip-label">{label ?? payload[0]?.name}</span>
      {payload.map((p: any, i: number) => (
        <span key={i} className="chart-tooltip-row">
          <i style={{ background: p.color || p.fill }} />
          {p.name}: <b>{p.value}</b>
        </span>
      ))}
    </div>
  )
}

export function DatasetCharts({ variables }: { variables: Variable[] }) {
  const missing = useMemo(() => {
    return variables
      .map(v => {
        const miss = num(v.missing)
        const n = num(v.n)
        const total = n + miss
        return {
          name: String(v.name),
          missing: miss,
          pct: total > 0 ? Math.round((miss / total) * 1000) / 10 : 0,
        }
      })
      .filter(d => d.missing > 0)
      .sort((a, b) => b.missing - a.missing)
      .slice(0, 10)
  }, [variables])

  const types = useMemo(() => {
    const counts: Record<string, number> = {}
    variables.forEach(v => {
      const t = String(v.type || 'unknown')
      counts[t] = (counts[t] || 0) + 1
    })
    return Object.entries(counts).map(([name, value]) => ({ name, value }))
  }, [variables])

  const cardinality = useMemo(() => {
    return variables
      .map(v => ({ name: String(v.name), unique: num(v.unique) }))
      .sort((a, b) => b.unique - a.unique)
      .slice(0, 10)
  }, [variables])

  const completeness = useMemo(() => {
    let complete = 0
    let missingCount = 0
    variables.forEach(v => {
      complete += num(v.n)
      missingCount += num(v.missing)
    })
    return [
      { name: 'Complete', value: complete },
      { name: 'Missing', value: missingCount },
    ]
  }, [variables])

  return (
    <div className="charts-grid">
      <ChartCard title="Missing values by variable" hint="Top variables with missing data">
        {missing.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={missing} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
              <CartesianGrid horizontal={false} stroke="var(--border)" />
              <XAxis type="number" stroke="var(--muted)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis type="category" dataKey="name" width={92} stroke="var(--muted)" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: 'var(--bg-soft)' }} />
              <Bar dataKey="missing" name="Missing" fill="#e11d48" radius={[0, 5, 5, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-empty">No missing values detected — clean dataset.</div>
        )}
      </ChartCard>

      <ChartCard title="Variable types" hint="Distribution of storage / measurement types">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={types} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={52} outerRadius={88} paddingAngle={3}>
              {types.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} stroke="var(--surface)" strokeWidth={2} />)}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Dataset completeness" hint="Complete vs missing observations overall">
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={completeness} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={52} outerRadius={88} paddingAngle={3}>
              <Cell fill="#0d9488" stroke="var(--surface)" strokeWidth={2} />
              <Cell fill="#f59e0b" stroke="var(--surface)" strokeWidth={2} />
            </Pie>
            <Tooltip content={<ChartTooltip />} />
            <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Unique values by variable" hint="Cardinality — helps spot IDs vs categories">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={cardinality} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
            <CartesianGrid horizontal={false} stroke="var(--border)" />
            <XAxis type="number" stroke="var(--muted)" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey="name" width={92} stroke="var(--muted)" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'var(--bg-soft)' }} />
            <Bar dataKey="unique" name="Unique" fill="#2563eb" radius={[0, 5, 5, 0]} barSize={16} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  )
}

export function RocChart({ points }: { points: Array<{ fpr: number; tpr: number }> }) {
  const data = [{ fpr: 0, tpr: 0 }, ...points, { fpr: 1, tpr: 1 }]
  return (
    <ChartCard title="ROC curve" hint="True positive rate vs false positive rate">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ left: 4, right: 16, top: 8, bottom: 8 }}>
          <CartesianGrid stroke="var(--border)" />
          <XAxis dataKey="fpr" type="number" domain={[0, 1]} stroke="var(--muted)" fontSize={11} tickLine={false} label={{ value: '1 - Specificity', position: 'insideBottom', offset: -4, fontSize: 11, fill: 'var(--muted)' }} />
          <YAxis type="number" domain={[0, 1]} stroke="var(--muted)" fontSize={11} tickLine={false} label={{ value: 'Sensitivity', angle: -90, position: 'insideLeft', fontSize: 11, fill: 'var(--muted)' }} />
          <Tooltip content={<ChartTooltip />} />
          <Line dataKey="tpr" name="Sensitivity" stroke="#0d9488" strokeWidth={2.5} dot={false} type="monotone" />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}
