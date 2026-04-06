import { useState, useEffect, createContext, useContext, useCallback, useRef } from "react"
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams, Link, useLocation } from "react-router-dom"
import axios from "axios"

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:#080C12; --bg2:#0D1520; --bg3:#111D2E; --bg4:#162035;
    --border:#1E2D42; --border2:#243650;
    --gold:#F0B429; --gold2:#D49520;
    --blue:#1A6FBF;
    --text:#E8EEF5; --text2:#8FA4BF; --text3:#4A6480; --text4:#2A4060;
    --red:#E53E3E; --orange:#DD6B20; --green:#38A169; --yellow:#D69E2E;
    --compliant:#38A169; --partial:#D69E2E; --atrisk:#DD6B20; --noncompliant:#E53E3E;
    --font-head:'Syne',sans-serif; --font-body:'Instrument Sans',sans-serif; --font-mono:'DM Mono',monospace;
    --radius:6px; --radius2:10px; --shadow:0 4px 24px rgba(0,0,0,0.5);
    --transition:all 0.18s ease;
  }
  html,body,#root { height:100%; background:var(--bg); color:var(--text); font-family:var(--font-body); font-size:14px; line-height:1.5; }
  ::-webkit-scrollbar { width:4px; height:4px; }
  ::-webkit-scrollbar-track { background:var(--bg2); }
  ::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }
  input,textarea,select { background:var(--bg3); border:1px solid var(--border); color:var(--text); font-family:var(--font-body); font-size:14px; padding:10px 14px; border-radius:var(--radius); width:100%; outline:none; transition:var(--transition); }
  input:focus,textarea:focus,select:focus { border-color:var(--gold); box-shadow:0 0 0 3px rgba(240,180,41,0.1); }
  input::placeholder,textarea::placeholder { color:var(--text3); }
  button { cursor:pointer; font-family:var(--font-body); transition:var(--transition); }
  a { color:inherit; text-decoration:none; }
  @keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
  @keyframes spin { to{transform:rotate(360deg)} }
  @keyframes slideIn { from{transform:translateX(120%);opacity:0} to{transform:translateX(0);opacity:1} }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .fade-up { animation:fadeUp 0.35s ease both; }
  .fade-up-1 { animation:fadeUp 0.35s 0.06s ease both; }
  .fade-up-2 { animation:fadeUp 0.35s 0.12s ease both; }
  .fade-up-3 { animation:fadeUp 0.35s 0.18s ease both; }
`

// API
const api = axios.create({ baseURL: "http://localhost:8000/api/v1" })
api.interceptors.request.use(cfg => {
  const t = localStorage.getItem("axiomgh_token")
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})
api.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) { localStorage.removeItem("axiomgh_token"); localStorage.removeItem("axiomgh_user"); window.location.href = "/login" }
  return Promise.reject(err)
})

// Auth
const AuthCtx = createContext(null)
const useAuth = () => useContext(AuthCtx)
function AuthProvider({ children }) {
  const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem("axiomgh_user")) } catch { return null } })
  const login = async (email, password) => {
    const { data } = await api.post("/auth/token/", { email, password })
    localStorage.setItem("axiomgh_token", data.access)
    localStorage.setItem("axiomgh_user", JSON.stringify(data.user))
    setUser(data.user); return data.user
  }
  const logout = () => { localStorage.removeItem("axiomgh_token"); localStorage.removeItem("axiomgh_user"); setUser(null) }
  return <AuthCtx.Provider value={{ user, login, logout }}>{children}</AuthCtx.Provider>
}

// Toast
const ToastCtx = createContext(null)
const useToast = () => useContext(ToastCtx)
function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const add = useCallback((msg, type = "success") => {
    const id = Date.now()
    setToasts(p => [...p, { id, msg, type }])
    setTimeout(() => setToasts(p => p.filter(t => t.id !== id)), 3500)
  }, [])
  const colorMap = { success: "var(--green)", error: "var(--red)", info: "var(--blue)", warning: "var(--orange)" }
  const iconMap = { success: "✓", error: "✕", info: "ℹ", warning: "⚠" }
  return (
    <ToastCtx.Provider value={{ toast: add }}>
      {children}
      <div style={{ position: "fixed", top: 20, right: 20, zIndex: 9999, display: "flex", flexDirection: "column", gap: 8, pointerEvents: "none" }}>
        {toasts.map(t => (
          <div key={t.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", background: "var(--bg2)", border: `1px solid ${colorMap[t.type]}35`, borderLeft: `3px solid ${colorMap[t.type]}`, borderRadius: "var(--radius2)", boxShadow: "var(--shadow)", animation: "slideIn 0.3s ease", minWidth: 280, maxWidth: 360, pointerEvents: "all" }}>
            <span style={{ color: colorMap[t.type], fontSize: 14, fontWeight: 700 }}>{iconMap[t.type]}</span>
            <span style={{ fontSize: 13, color: "var(--text)", flex: 1 }}>{t.msg}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

// Design components
const Card = ({ children, style, onClick, hover }) => (
  <div onClick={onClick} style={{ background: "var(--bg2)", border: "1px solid var(--border)", borderRadius: "var(--radius2)", padding: 24, transition: hover ? "border-color 0.2s, box-shadow 0.2s" : undefined, cursor: onClick ? "pointer" : undefined, ...style }}
    onMouseEnter={hover ? e => { e.currentTarget.style.borderColor = "var(--border2)"; e.currentTarget.style.boxShadow = "var(--shadow)" } : undefined}
    onMouseLeave={hover ? e => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.boxShadow = "none" } : undefined}
  >{children}</div>
)

const Badge = ({ children, color = "var(--blue)", dot }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 5, background: color + "18", color, border: `1px solid ${color}35`, borderRadius: 4, padding: "2px 8px", fontSize: 10, fontFamily: "var(--font-mono)", fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase" }}>
    {dot && <span style={{ width: 5, height: 5, borderRadius: "50%", background: color, display: "inline-block" }} />}
    {children}
  </span>
)

const RatingBadge = ({ rating }) => {
  const map = { compliant: ["Compliant", "var(--compliant)"], partial: ["Partial", "var(--partial)"], at_risk: ["At Risk", "var(--atrisk)"], non_compliant: ["Non-Compliant", "var(--noncompliant)"] }
  const [label, color] = map[rating] || [rating, "var(--text2)"]
  return <Badge color={color} dot>{label}</Badge>
}

const Spinner = ({ size = 18 }) => <div style={{ width: size, height: size, border: "2px solid var(--border2)", borderTopColor: "var(--gold)", borderRadius: "50%", animation: "spin 0.65s linear infinite", display: "inline-block", flexShrink: 0 }} />

const Btn = ({ children, onClick, variant = "primary", disabled, style, type = "button", size = "md" }) => {
  const sizes = { sm: { padding: "6px 14px", fontSize: 12 }, md: { padding: "10px 20px", fontSize: 14 }, lg: { padding: "13px 28px", fontSize: 15 } }
  const variants = { primary: { background: "var(--gold)", color: "#080C12", border: "none" }, secondary: { background: "var(--bg3)", color: "var(--text)", border: "1px solid var(--border2)" }, danger: { background: "var(--red)", color: "white", border: "none" }, ghost: { background: "transparent", color: "var(--text2)", border: "1px solid var(--border)" }, success: { background: "var(--green)", color: "white", border: "none" } }
  return (
    <button type={type} onClick={onClick} disabled={disabled} style={{ ...sizes[size], fontWeight: 600, borderRadius: "var(--radius)", display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8, letterSpacing: "0.02em", transition: "var(--transition)", opacity: disabled ? 0.45 : 1, cursor: disabled ? "not-allowed" : "pointer", ...variants[variant], ...style }}>
      {children}
    </button>
  )
}

const ProgressBar = ({ value, max = 100, color, height = 6 }) => {
  const pct = Math.min(Math.max((value / max) * 100, 0), 100)
  const c = color || (pct >= 80 ? "var(--compliant)" : pct >= 60 ? "var(--partial)" : pct >= 40 ? "var(--atrisk)" : "var(--noncompliant)")
  return <div style={{ background: "var(--bg3)", borderRadius: 99, height, overflow: "hidden" }}><div style={{ width: `${pct}%`, height: "100%", background: c, borderRadius: 99, transition: "width 0.7s ease" }} /></div>
}

const ScoreRing = ({ score, max = 1000, size = 140 }) => {
  const pct = Math.min(score / max, 1)
  const r = (size / 2) - 14
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - pct)
  const color = pct >= 0.8 ? "var(--compliant)" : pct >= 0.6 ? "var(--partial)" : pct >= 0.4 ? "var(--atrisk)" : "var(--noncompliant)"
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--bg3)" strokeWidth={10} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={10} strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round" style={{ transition: "stroke-dashoffset 1.2s ease" }} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontFamily: "var(--font-head)", fontSize: size * 0.19, fontWeight: 800, color, lineHeight: 1 }}>{Math.round(score)}</span>
        <span style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>/ {max}</span>
      </div>
    </div>
  )
}

const StatCard = ({ label, value, unit, color = "var(--gold)", icon, sub }) => (
  <Card style={{ padding: "18px 20px" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
      <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em" }}>{label.toUpperCase()}</div>
      {icon && <span style={{ fontSize: 14, opacity: 0.4 }}>{icon}</span>}
    </div>
    <div style={{ fontFamily: "var(--font-head)", fontSize: 24, fontWeight: 800, color, lineHeight: 1 }}>
      {value}{unit && <span style={{ fontSize: 12, fontWeight: 400, color: "var(--text3)", marginLeft: 4 }}>{unit}</span>}
    </div>
    {sub && <div style={{ fontSize: 11, color: "var(--text3)", marginTop: 5 }}>{sub}</div>}
  </Card>
)

const EmptyState = ({ icon = "◈", title, desc, action, actionLabel }) => (
  <Card style={{ textAlign: "center", padding: "60px 40px", background: "linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%)" }}>
    <div style={{ fontSize: 44, marginBottom: 14, opacity: 0.35 }}>{icon}</div>
    <h3 style={{ fontFamily: "var(--font-head)", fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{title}</h3>
    <p style={{ color: "var(--text2)", lineHeight: 1.6, maxWidth: 380, margin: "0 auto 22px", fontSize: 13 }}>{desc}</p>
    {action && <Btn onClick={action}>{actionLabel}</Btn>}
  </Card>
)

const PageHeader = ({ label, title, subtitle, actions }) => (
  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 26 }}>
    <div>
      {label && <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.12em", marginBottom: 5 }}>{label}</div>}
      <h1 style={{ fontFamily: "var(--font-head)", fontSize: 24, fontWeight: 700, color: "var(--text)", lineHeight: 1.2 }}>{title}</h1>
      {subtitle && <p style={{ fontSize: 12, color: "var(--text3)", marginTop: 4 }}>{subtitle}</p>}
    </div>
    {actions && <div style={{ display: "flex", gap: 10, alignItems: "center", flexShrink: 0, marginLeft: 20 }}>{actions}</div>}
  </div>
)

const Tabs = ({ tabs, active, onChange }) => (
  <div style={{ display: "flex", gap: 2, marginBottom: 18, borderBottom: "1px solid var(--border)" }}>
    {tabs.map(([key, label]) => (
      <button key={key} onClick={() => onChange(key)} style={{ padding: "9px 18px", border: "none", background: "transparent", color: active === key ? "var(--gold)" : "var(--text3)", fontSize: 12, fontWeight: active === key ? 600 : 400, cursor: "pointer", borderBottom: `2px solid ${active === key ? "var(--gold)" : "transparent"}`, transition: "var(--transition)", fontFamily: "var(--font-body)" }}>
        {label}
      </button>
    ))}
  </div>
)

// Sidebar
const NAV = [
  { path: "/dashboard",   icon: "▣", label: "Dashboard" },
  { path: "/assessments", icon: "◈", label: "Assessments" },
  { path: "/reports",     icon: "▤", label: "Reports" },
  { path: "/benchmarks",  icon: "◎", label: "Benchmarks" },
  { path: "/settings",    icon: "⚙", label: "Settings" },
]

function Sidebar() {
  const { user, logout } = useAuth()
  const loc = useLocation()
  return (
    <aside style={{ width: 220, background: "var(--bg2)", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column", height: "100vh", position: "fixed", left: 0, top: 0, zIndex: 100 }}>
      <div style={{ padding: "20px 18px 16px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ fontFamily: "var(--font-head)", fontSize: 20, fontWeight: 800, color: "var(--gold)", letterSpacing: "-0.02em" }}>Axiom<span style={{ color: "var(--text3)", fontWeight: 400 }}>GH</span></div>
        <div style={{ fontSize: 9, color: "var(--text4)", fontFamily: "var(--font-mono)", marginTop: 3, letterSpacing: "0.12em" }}>CISD 2026 COMPLIANCE</div>
      </div>
      <nav style={{ flex: 1, padding: "10px 8px", display: "flex", flexDirection: "column", gap: 2 }}>
        {NAV.map(item => {
          const active = loc.pathname.startsWith(item.path)
          return (
            <Link key={item.path} to={item.path} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 10px", borderRadius: "var(--radius)", textDecoration: "none", background: active ? "rgba(240,180,41,0.08)" : "transparent", color: active ? "var(--gold)" : "var(--text3)", borderLeft: `2px solid ${active ? "var(--gold)" : "transparent"}`, fontSize: 13, fontWeight: active ? 600 : 400, transition: "var(--transition)" }}>
              <span style={{ fontSize: 14, width: 16, textAlign: "center" }}>{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>
      <div style={{ padding: "12px 16px", borderTop: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 9, marginBottom: 9 }}>
          <div style={{ width: 30, height: 30, borderRadius: "50%", background: "var(--gold)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 12, color: "#080C12", flexShrink: 0 }}>{user?.first_name?.[0]}{user?.last_name?.[0]}</div>
          <div style={{ overflow: "hidden" }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{user?.first_name} {user?.last_name}</div>
            <div style={{ fontSize: 9, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{user?.role?.toUpperCase()}</div>
          </div>
        </div>
        <button onClick={logout} style={{ background: "none", border: "none", color: "var(--text3)", fontSize: 11, padding: 0, cursor: "pointer" }}>Sign out →</button>
      </div>
    </aside>
  )
}

function AppShell({ children }) {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <main style={{ marginLeft: 220, flex: 1, minHeight: "100vh", padding: "26px 30px", maxWidth: "calc(100vw - 220px)" }}>{children}</main>
    </div>
  )
}

// Login
function LoginPage() {
  const { login } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState("")
  const [pass, setPass] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [showPass, setShowPass] = useState(false)

  const submit = async e => {
    e.preventDefault(); setLoading(true); setError("")
    try { await login(email, pass); nav("/dashboard") }
    catch { setError("Invalid email or password. Please try again.") }
    finally { setLoading(false) }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", backgroundImage: "radial-gradient(ellipse at 20% 50%, rgba(13,30,58,0.8) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(26,26,10,0.5) 0%, transparent 50%)" }}>
      <div style={{ position: "fixed", inset: 0, opacity: 0.02, backgroundImage: "linear-gradient(var(--text) 1px, transparent 1px), linear-gradient(90deg, var(--text) 1px, transparent 1px)", backgroundSize: "48px 48px", pointerEvents: "none" }} />
      <div className="fade-up" style={{ width: 420, position: "relative", zIndex: 1 }}>
        <div style={{ textAlign: "center", marginBottom: 34 }}>
          <div style={{ fontFamily: "var(--font-head)", fontSize: 38, fontWeight: 800, color: "var(--gold)", letterSpacing: "-0.03em", lineHeight: 1 }}>AxiomGH</div>
          <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", marginTop: 6, letterSpacing: "0.14em" }}>CISD 2026 COMPLIANCE INTELLIGENCE</div>
        </div>
        <Card>
          <h2 style={{ fontFamily: "var(--font-head)", fontSize: 17, fontWeight: 700, marginBottom: 20 }}>Sign in to your institution</h2>
          <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", display: "block", marginBottom: 6 }}>EMAIL ADDRESS</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="ciso@yourbank.com.gh" required autoFocus />
            </div>
            <div>
              <label style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", display: "block", marginBottom: 6 }}>PASSWORD</label>
              <div style={{ position: "relative" }}>
                <input type={showPass ? "text" : "password"} value={pass} onChange={e => setPass(e.target.value)} placeholder="••••••••" required style={{ paddingRight: 50 }} />
                <button type="button" onClick={() => setShowPass(!showPass)} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", color: "var(--text3)", fontSize: 11, padding: 0 }}>{showPass ? "Hide" : "Show"}</button>
              </div>
            </div>
            {error && <div style={{ background: "rgba(229,62,62,0.08)", border: "1px solid rgba(229,62,62,0.2)", borderRadius: "var(--radius)", padding: "10px 14px", fontSize: 12, color: "var(--red)" }}>{error}</div>}
            <Btn type="submit" disabled={loading} style={{ marginTop: 4, width: "100%", padding: "12px 20px" }}>
              {loading ? <><Spinner size={15} /> Signing in...</> : "Sign in →"}
            </Btn>
          </form>
        </Card>
        <div style={{ textAlign: "center", marginTop: 16, fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>Secured · Bank of Ghana CISD 2026 Compliant</div>
      </div>
    </div>
  )
}

// Dashboard
function Dashboard() {
  const { user } = useAuth()
  const nav = useNavigate()
  const [state, setState] = useState({ assessments: [], latest: null, scores: [], loading: true })

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get("/assessments/")
        const all = data.results || data
        const latest = all.find(a => a.status === "completed") || null
        let scores = []
        if (latest) { try { const { data: sc } = await api.get(`/assessments/${latest.id}/scores/`); scores = Array.isArray(sc) ? sc : [] } catch {} }
        setState({ assessments: all, latest, scores, loading: false })
      } catch { setState(s => ({ ...s, loading: false })) }
    }
    load()
  }, [])

  const { assessments, latest, scores, loading } = state
  const pct = latest ? parseFloat(latest.overall_percentage || 0) : 0
  const rating = pct >= 80 ? "compliant" : pct >= 60 ? "partial" : pct >= 40 ? "at_risk" : "non_compliant"
  const totalGaps = scores.reduce((a, s) => a + (s.gap_count || 0), 0)
  const inProgress = assessments.filter(a => a.status === "in_progress")

  if (loading) return <AppShell><div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}><Spinner size={30} /></div></AppShell>

  return (
    <AppShell>
      <PageHeader label="COMPLIANCE INTELLIGENCE DASHBOARD" title={user?.institution_name || "Your Institution"}
        subtitle={latest ? `Last assessment: ${new Date(latest.completed_at).toLocaleDateString("en-GH", { day: "numeric", month: "long", year: "numeric" })}` : "No completed assessment yet"}
        actions={<Btn onClick={() => nav("/assessments/new")}>+ New Assessment</Btn>} />

      {inProgress.length > 0 && (
        <div className="fade-up" style={{ marginBottom: 18 }}>
          <Card style={{ background: "rgba(240,180,41,0.05)", borderColor: "rgba(240,180,41,0.2)", padding: "13px 18px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 13, color: "var(--gold)", animation: "pulse 2s infinite" }}>◉</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--gold)" }}>Assessment In Progress</div>
                  <div style={{ fontSize: 11, color: "var(--text3)" }}>{inProgress.length} unfinished assessment{inProgress.length > 1 ? "s" : ""} — click to continue</div>
                </div>
              </div>
              <Btn size="sm" onClick={() => nav(`/assessments/${inProgress[0].id}`)}>Continue →</Btn>
            </div>
          </Card>
        </div>
      )}

      {!latest ? (
        <EmptyState icon="◈" title="No Completed Assessment" desc="Start your first CISD 2026 compliance assessment to see your institution's full compliance posture across all 23 sections." action={() => nav("/assessments/new")} actionLabel="Start Assessment →" />
      ) : (
        <>
          <div className="fade-up-1" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 18 }}>
            <StatCard label="Overall Score" value={Math.round(latest.overall_score || 0)} unit="/ 1000" color="var(--gold)" icon="◉" />
            <StatCard label="Compliance Rate" value={pct.toFixed(1) + "%"} color={`var(--${rating === "compliant" ? "compliant" : rating === "partial" ? "partial" : rating === "at_risk" ? "atrisk" : "noncompliant"})`} icon="▣" />
            <StatCard label="Total Gaps" value={totalGaps} color={totalGaps > 0 ? "var(--noncompliant)" : "var(--compliant)"} icon="⚠" sub={totalGaps === 0 ? "Fully compliant" : "Require remediation"} />
            <StatCard label="Sections" value={scores.length} unit="/ 23" color="var(--blue)" icon="◈" />
          </div>

          <div className="fade-up-2" style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 18, marginBottom: 18 }}>
            <Card style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14, padding: 24 }}>
              <ScoreRing score={latest.overall_score || 0} size={155} />
              <RatingBadge rating={rating} />
              <Btn variant="secondary" size="sm" onClick={() => nav(`/assessments/${latest.id}/results`)} style={{ width: "100%" }}>View Full Results</Btn>
              <Btn size="sm" onClick={async () => {
                try {
                  const token = localStorage.getItem("axiomgh_token")
                  const res = await fetch(`http://localhost:8000/api/v1/assessments/${latest.id}/pdf_report/`, { headers: { Authorization: `Bearer ${token}` } })
                  const blob = await res.blob(); const url = window.URL.createObjectURL(blob)
                  const a = document.createElement("a"); a.href = url; a.download = "AxiomGH_Report.pdf"; a.click()
                } catch {}
              }} style={{ width: "100%" }}>↓ Download PDF</Btn>
            </Card>
            <Card>
              <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 14 }}>SECTION COMPLIANCE BREAKDOWN</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 9, maxHeight: 320, overflowY: "auto" }}>
                {scores.length === 0 ? <div style={{ fontSize: 13, color: "var(--text3)", textAlign: "center", padding: "20px 0" }}>No section scores yet</div> :
                  scores.map(sc => {
                    const p = parseFloat(sc.percentage || 0)
                    return (
                      <div key={sc.id || sc.section} style={{ display: "grid", gridTemplateColumns: "26px 1fr 56px 54px", gap: 10, alignItems: "center" }}>
                        <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text3)" }}>{sc.section_number}</span>
                        <div><div style={{ fontSize: 11, color: "var(--text)", marginBottom: 3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{sc.section_title}</div><ProgressBar value={p} height={4} /></div>
                        <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, textAlign: "right", color: p >= 80 ? "var(--compliant)" : p >= 60 ? "var(--partial)" : p >= 40 ? "var(--atrisk)" : "var(--noncompliant)", fontWeight: 600 }}>{p.toFixed(0)}%</div>
                        <div style={{ textAlign: "right" }}>{(sc.gap_count || 0) > 0 && <span style={{ fontSize: 9, color: "var(--noncompliant)", fontFamily: "var(--font-mono)" }}>{sc.gap_count}g</span>}</div>
                      </div>
                    )
                  })}
              </div>
            </Card>
          </div>

          <div className="fade-up-3">
            <Card>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em" }}>ASSESSMENT HISTORY</div>
                <Btn size="sm" variant="ghost" onClick={() => nav("/assessments")}>View All →</Btn>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)" }}>
                    {["Date", "Status", "Score", "Rate", ""].map(h => <th key={h} style={{ textAlign: "left", fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", padding: "6px 10px", letterSpacing: "0.06em", fontWeight: 500 }}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {assessments.slice(0, 5).map(a => (
                    <tr key={a.id} style={{ borderBottom: "1px solid rgba(30,45,66,0.4)" }}>
                      <td style={{ padding: "10px", fontSize: 12, color: "var(--text2)" }}>{new Date(a.started_at).toLocaleDateString("en-GH", { day: "numeric", month: "short", year: "numeric" })}</td>
                      <td style={{ padding: "10px" }}><Badge color={a.status === "completed" ? "var(--compliant)" : "var(--partial)"}>{a.status.replace("_", " ")}</Badge></td>
                      <td style={{ padding: "10px", fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--gold)", fontWeight: 700 }}>{a.overall_score ? Math.round(a.overall_score) : "—"}</td>
                      <td style={{ padding: "10px", fontSize: 12, color: "var(--text3)" }}>{a.overall_percentage ? parseFloat(a.overall_percentage).toFixed(1) + "%" : "—"}</td>
                      <td style={{ padding: "10px", textAlign: "right" }}>
                        <button onClick={() => nav(a.status === "completed" ? `/assessments/${a.id}/results` : `/assessments/${a.id}`)} style={{ background: "none", border: "none", color: "var(--gold)", fontSize: 12, cursor: "pointer" }}>{a.status === "completed" ? "Results →" : "Continue →"}</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  )
}

// Assessments List
function AssessmentsList() {
  const nav = useNavigate()
  const [assessments, setAssessments] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("all")

  useEffect(() => { api.get("/assessments/").then(({ data }) => setAssessments(data.results || data)).catch(console.error).finally(() => setLoading(false)) }, [])

  const filtered = filter === "all" ? assessments : assessments.filter(a => a.status === filter)

  return (
    <AppShell>
      <PageHeader label="ASSESSMENTS" title="Assessment History" subtitle={`${assessments.length} total`} actions={<Btn onClick={() => nav("/assessments/new")}>+ New Assessment</Btn>} />
      <div className="fade-up" style={{ display: "flex", gap: 8, marginBottom: 18 }}>
        {[["all", `All (${assessments.length})`], ["completed", `Completed (${assessments.filter(a => a.status === "completed").length})`], ["in_progress", `In Progress (${assessments.filter(a => a.status === "in_progress").length})`]].map(([f, l]) => (
          <button key={f} onClick={() => setFilter(f)} style={{ padding: "6px 14px", borderRadius: "var(--radius)", border: `1px solid ${filter === f ? "var(--gold)" : "var(--border)"}`, background: filter === f ? "rgba(240,180,41,0.08)" : "var(--bg3)", color: filter === f ? "var(--gold)" : "var(--text3)", fontSize: 12, fontWeight: filter === f ? 600 : 400, cursor: "pointer" }}>{l}</button>
        ))}
      </div>
      {loading ? <div style={{ display: "flex", justifyContent: "center", paddingTop: 60 }}><Spinner size={28} /></div> :
        filtered.length === 0 ? <EmptyState icon="◈" title="No Assessments" desc="Start your first CISD 2026 compliance assessment." action={() => nav("/assessments/new")} actionLabel="Start Assessment" /> :
        <div className="fade-up-1" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {filtered.map(a => (
            <Card key={a.id} hover onClick={() => nav(a.status === "completed" ? `/assessments/${a.id}/results` : `/assessments/${a.id}`)} style={{ padding: "16px 20px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <div style={{ width: 38, height: 38, borderRadius: "var(--radius)", background: a.status === "completed" ? "rgba(56,161,105,0.1)" : "rgba(240,180,41,0.1)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, color: a.status === "completed" ? "var(--compliant)" : "var(--gold)" }}>{a.status === "completed" ? "✓" : "◉"}</div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 3 }}>{a.institution_name}</div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <Badge color={a.status === "completed" ? "var(--compliant)" : "var(--partial)"}>{a.status.replace("_", " ")}</Badge>
                      <span style={{ fontSize: 11, color: "var(--text3)" }}>{new Date(a.started_at).toLocaleDateString("en-GH")}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                  {a.overall_score && <div style={{ textAlign: "right" }}><div style={{ fontFamily: "var(--font-head)", fontSize: 20, fontWeight: 800, color: "var(--gold)" }}>{Math.round(a.overall_score)}</div><div style={{ fontSize: 9, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>/ 1000 pts</div></div>}
                  <span style={{ color: "var(--text3)", fontSize: 16 }}>→</span>
                </div>
              </div>
            </Card>
          ))}
        </div>}
    </AppShell>
  )
}

// New Assessment
function NewAssessment() {
  const nav = useNavigate()
  const { user } = useAuth()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  const start = async () => {
    setLoading(true)
    try { const { data } = await api.post("/assessments/", { institution: user.institution, status: "in_progress" }); toast("Assessment started", "success"); nav(`/assessments/${data.id}`) }
    catch { toast("Failed to start assessment. Please try again.", "error") }
    finally { setLoading(false) }
  }

  return (
    <AppShell>
      <div style={{ maxWidth: 600, margin: "0 auto", paddingTop: 10 }}>
        <PageHeader label="NEW ASSESSMENT" title="CISD 2026 Compliance Assessment" />
        <Card style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 14 }}>WHAT THIS COVERS</div>
          {[["◈", "23 Sections", "All parts of the BoG CISD 2026 directive including 3 new 2026 additions"],["▣", "172 Questions", "Yes / Partial / No / N/A responses with optional evidence notes"],["◉", "Auto Scoring", "Weighted compliance score out of 1000 computed on completion"],["▤", "Gap Report", "Prioritised compliance gaps sorted by risk level and severity"],["◎", "PDF Export", "Professional board-ready report downloadable as PDF"]].map(([icon, title, desc]) => (
            <div key={title} style={{ display: "flex", gap: 12, alignItems: "flex-start", marginBottom: 12 }}>
              <div style={{ width: 26, height: 26, borderRadius: "50%", background: "rgba(240,180,41,0.08)", border: "1px solid rgba(240,180,41,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, flexShrink: 0 }}>{icon}</div>
              <div><div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 1 }}>{title}</div><div style={{ fontSize: 12, color: "var(--text2)" }}>{desc}</div></div>
            </div>
          ))}
        </Card>
        <Card style={{ marginBottom: 18, background: "rgba(240,180,41,0.03)", borderColor: "rgba(240,180,41,0.15)" }}>
          <div style={{ fontSize: 10, color: "var(--gold)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 6 }}>NOTE</div>
          <p style={{ fontSize: 12, color: "var(--text2)", lineHeight: 1.6 }}>Answers save automatically. You can pause and resume at any time. The assessment is scored only when you click Complete Assessment.</p>
        </Card>
        <div style={{ display: "flex", gap: 10 }}>
          <Btn onClick={start} disabled={loading} style={{ flex: 1, padding: "12px 20px" }}>{loading ? <><Spinner size={15} /> Starting...</> : "Begin Assessment →"}</Btn>
          <Btn variant="ghost" onClick={() => nav("/assessments")}>Cancel</Btn>
        </div>
      </div>
    </AppShell>
  )
}

// Assessment Flow
function AssessmentFlow() {
  const { id } = useParams()
  const nav = useNavigate()
  const { toast } = useToast()
  const [sections, setSections] = useState([])
  const [currentSection, setCurrentSection] = useState(0)
  const [responses, setResponses] = useState({})
  const [saving, setSaving] = useState(false)
  const [savedOk, setSavedOk] = useState(false)
  const [completing, setCompleting] = useState(false)
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)
  const saveTimer = useRef(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [{ data: ass }, { data: resp }] = await Promise.all([api.get(`/assessments/${id}/`), api.get(`/assessments/${id}/responses/`)])
        if (ass.status === "completed") { nav(`/assessments/${id}/results`); return }
        setAssessment(ass); setSections(resp)
        const map = {}
        resp.forEach(sec => sec.responses.forEach(r => { map[r.question] = { answer: r.answer || "unanswered", notes: r.notes || "" } }))
        setResponses(map)
      } catch { toast("Failed to load assessment", "error") }
      finally { setLoading(false) }
    }
    load()
  }, [id])

  const totalQ = sections.reduce((a, s) => a + s.responses.length, 0)
  const answeredQ = Object.values(responses).filter(r => r.answer !== "unanswered").length
  const pct = totalQ > 0 ? (answeredQ / totalQ) * 100 : 0

  const doSave = useCallback(async (qId, answer, notes) => {
    setSaving(true)
    try { await api.post("/responses/bulk_save/", { assessment_id: id, responses: [{ question_id: qId, answer, notes }] }); setSavedOk(true); setTimeout(() => setSavedOk(false), 2000) }
    catch { toast("Save failed", "error") }
    finally { setSaving(false) }
  }, [id])

  const setAnswer = (qId, answer) => {
    setResponses(p => ({ ...p, [qId]: { ...p[qId], answer } }))
    doSave(qId, answer, responses[qId]?.notes || "")
  }

  const setNotes = (qId, notes) => {
    setResponses(p => ({ ...p, [qId]: { ...p[qId], notes } }))
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => doSave(qId, responses[qId]?.answer || "unanswered", notes), 1200)
  }

  const complete = async () => {
    setCompleting(true)
    try { await api.post(`/assessments/${id}/complete/`); toast("Assessment completed!", "success"); nav(`/assessments/${id}/results`) }
    catch (e) { toast(e.response?.data?.error || "Failed to complete", "error") }
    finally { setCompleting(false) }
  }

  if (loading) return <AppShell><div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}><Spinner size={30} /></div></AppShell>
  const section = sections[currentSection]

  return (
    <AppShell>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18, paddingBottom: 14, borderBottom: "1px solid var(--border)" }}>
        <div>
          <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.12em", marginBottom: 3 }}>CISD 2026 ASSESSMENT</div>
          <h1 style={{ fontFamily: "var(--font-head)", fontSize: 17, fontWeight: 700 }}>{assessment?.institution_name}</h1>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ textAlign: "right", minWidth: 130 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 6, marginBottom: 4 }}>
              {saving ? <><Spinner size={10} /><span style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>Saving...</span></> :
               savedOk ? <span style={{ fontSize: 10, color: "var(--compliant)", fontFamily: "var(--font-mono)" }}>✓ Saved</span> :
               <span style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{answeredQ}/{totalQ} answered</span>}
            </div>
            <ProgressBar value={pct} height={4} color="var(--gold)" />
            <div style={{ fontSize: 9, color: "var(--text3)", fontFamily: "var(--font-mono)", marginTop: 2, textAlign: "right" }}>{pct.toFixed(0)}%</div>
          </div>
          <Btn onClick={complete} disabled={completing}>{completing ? <><Spinner size={14} /> Completing...</> : "Complete Assessment"}</Btn>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "210px 1fr", gap: 18 }}>
        <div style={{ position: "sticky", top: 0, alignSelf: "start" }}>
          <Card style={{ padding: "10px 6px" }}>
            <div style={{ fontSize: 9, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 8, padding: "0 6px" }}>SECTIONS</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 1, maxHeight: "calc(100vh - 210px)", overflowY: "auto" }}>
              {sections.map((sec, i) => {
                const done = sec.responses.filter(r => responses[r.question]?.answer !== "unanswered").length
                const total = sec.responses.length
                const active = currentSection === i
                return (
                  <button key={sec.section_id} onClick={() => setCurrentSection(i)} style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 8px", borderRadius: "var(--radius)", border: "none", textAlign: "left", cursor: "pointer", background: active ? "rgba(240,180,41,0.1)" : "transparent", borderLeft: `2px solid ${active ? "var(--gold)" : "transparent"}`, transition: "var(--transition)" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: active ? "var(--gold)" : "var(--text3)", width: 16, flexShrink: 0 }}>{sec.section_number}</span>
                    <span style={{ fontSize: 10, color: active ? "var(--gold)" : "var(--text2)", flex: 1, lineHeight: 1.3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{sec.section_title}</span>
                    <span style={{ fontSize: 8, fontFamily: "var(--font-mono)", color: done === total ? "var(--compliant)" : "var(--text3)", flexShrink: 0 }}>{done}/{total}</span>
                  </button>
                )
              })}
            </div>
          </Card>
        </div>

        {section && (
          <div key={currentSection} className="fade-up">
            <Card style={{ marginBottom: 14, padding: "14px 18px", borderLeft: "3px solid var(--gold)", background: "linear-gradient(90deg, rgba(240,180,41,0.04) 0%, var(--bg2) 50%)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--gold)" }}>SECTION {section.section_number}</span>
                <Badge color={section.section_risk_level === "critical" ? "var(--noncompliant)" : section.section_risk_level === "high" ? "var(--atrisk)" : section.section_risk_level === "medium" ? "var(--partial)" : "var(--compliant)"}>{section.section_risk_level}</Badge>
                <Badge color="var(--blue)">{section.section_weight} weight</Badge>
              </div>
              <h2 style={{ fontFamily: "var(--font-head)", fontSize: 15, fontWeight: 700 }}>{section.section_title}</h2>
            </Card>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {section.responses.map(resp => {
                const cur = responses[resp.question] || { answer: "unanswered", notes: "" }
                const answered = cur.answer !== "unanswered"
                const bc = !answered ? "var(--border)" : cur.answer === "yes" ? "var(--compliant)" : cur.answer === "partial" ? "var(--partial)" : cur.answer === "no" ? "var(--noncompliant)" : "var(--text3)"
                return (
                  <Card key={resp.id} style={{ borderLeft: `3px solid ${bc}`, padding: "14px 18px", transition: "border-color 0.2s" }}>
                    <div style={{ display: "flex", gap: 10 }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text3)", flexShrink: 0, paddingTop: 2, width: 30 }}>{resp.question_number}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, color: "var(--text)", lineHeight: 1.6, marginBottom: 12 }}>{resp.question_text}</div>
                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: answered && cur.answer !== "na" ? 8 : 0 }}>
                          {[["yes", "Yes", "var(--compliant)"], ["partial", "Partial", "var(--partial)"], ["no", "No", "var(--noncompliant)"], ["na", "N/A", "var(--text3)"]].map(([val, label, color]) => {
                            const sel = cur.answer === val
                            return <button key={val} onClick={() => setAnswer(resp.question, val)} style={{ padding: "5px 14px", borderRadius: "var(--radius)", border: `1px solid ${sel ? color : "var(--border)"}`, background: sel ? color + "18" : "var(--bg3)", color: sel ? color : "var(--text3)", fontSize: 12, fontWeight: sel ? 600 : 400, transition: "var(--transition)", cursor: "pointer" }}>{label}</button>
                          })}
                          <div style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text3)", display: "flex", alignItems: "center" }}>{resp.max_points}pts</div>
                        </div>
                        {answered && cur.answer !== "na" && <textarea value={cur.notes} onChange={e => setNotes(resp.question, e.target.value)} placeholder="Add notes, evidence references, or planned actions..." rows={2} style={{ fontSize: 12, resize: "vertical", marginTop: 4 }} />}
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 18, paddingBottom: 40 }}>
              <Btn variant="ghost" onClick={() => setCurrentSection(Math.max(0, currentSection - 1))} disabled={currentSection === 0}>← Previous</Btn>
              {currentSection < sections.length - 1
                ? <Btn onClick={() => setCurrentSection(currentSection + 1)}>Next Section →</Btn>
                : <Btn onClick={complete} disabled={completing}>{completing ? <Spinner size={14} /> : "Complete Assessment →"}</Btn>}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}

// Results
function Results() {
  const { id } = useParams()
  const nav = useNavigate()
  const { toast } = useToast()
  const [assessment, setAssessment] = useState(null)
  const [scores, setScores] = useState([])
  const [gaps, setGaps] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [tab, setTab] = useState("overview")

  useEffect(() => {
    const load = async () => {
      try {
        const { data: ass } = await api.get(`/assessments/${id}/`)
        setAssessment(ass)
        try { const { data: sc } = await api.get(`/assessments/${id}/scores/`); setScores(Array.isArray(sc) ? sc : []) } catch {}
        try { const { data: gp } = await api.get(`/assessments/${id}/gaps/`); setGaps(Array.isArray(gp) ? gp : []) } catch {}
      } catch { toast("Failed to load results", "error") }
      finally { setLoading(false) }
    }
    load()
  }, [id])

  const downloadPDF = async () => {
    setDownloading(true)
    try {
      const token = localStorage.getItem("axiomgh_token")
      const res = await fetch(`http://localhost:8000/api/v1/assessments/${id}/pdf_report/`, { headers: { Authorization: `Bearer ${token}` } })
      if (!res.ok) throw new Error()
      const blob = await res.blob(); const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a"); a.href = url
      a.download = `AxiomGH_CISD2026_${assessment?.institution_name?.replace(/\s/g, "_")}_Report.pdf`
      a.click(); window.URL.revokeObjectURL(url)
      toast("PDF downloaded successfully", "success")
    } catch { toast("Failed to download PDF", "error") }
    finally { setDownloading(false) }
  }

  if (loading) return <AppShell><div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}><Spinner size={30} /></div></AppShell>

  const pct = parseFloat(assessment?.overall_percentage || 0)
  const rating = pct >= 80 ? "compliant" : pct >= 60 ? "partial" : pct >= 40 ? "at_risk" : "non_compliant"
  const critGaps = gaps.filter(g => g.section_risk_level === "critical" && g.answer === "no")
  const highGaps = gaps.filter(g => g.section_risk_level === "high" && g.answer === "no")
  const partGaps = gaps.filter(g => g.answer === "partial")
  const noGaps = gaps.filter(g => g.answer === "no")

  return (
    <AppShell>
      <PageHeader label="ASSESSMENT RESULTS" title={assessment?.institution_name}
        subtitle={assessment?.completed_at ? `Completed ${new Date(assessment.completed_at).toLocaleDateString("en-GH", { day: "numeric", month: "long", year: "numeric" })}` : ""}
        actions={<>
          <Btn variant="secondary" size="sm" onClick={() => nav(`/assessments/${id}`)}>← Back to Assessment</Btn>
          <Btn size="sm" onClick={downloadPDF} disabled={downloading}>{downloading ? <><Spinner size={13} /> Generating...</> : "↓ Download PDF"}</Btn>
        </>} />

      <div className="fade-up" style={{ display: "grid", gridTemplateColumns: "250px 1fr", gap: 14, marginBottom: 18 }}>
        <Card style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 24, gap: 13, background: "linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%)" }}>
          <ScoreRing score={assessment?.overall_score || 0} size={160} />
          <RatingBadge rating={rating} />
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: "var(--gold)", fontFamily: "var(--font-head)" }}>{pct.toFixed(1)}%</div>
            <div style={{ fontSize: 10, color: "var(--text3)" }}>Overall Compliance</div>
          </div>
        </Card>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            <StatCard label="Critical Gaps" value={critGaps.length} color="var(--noncompliant)" icon="⚠" sub="Immediate action" />
            <StatCard label="High Risk Gaps" value={highGaps.length} color="var(--atrisk)" icon="▲" sub="High priority" />
            <StatCard label="Partial Answers" value={partGaps.length} color="var(--partial)" icon="◑" sub="Partially compliant" />
          </div>
          <Card style={{ flex: 1 }}>
            <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 12 }}>COMPLIANCE BY RISK LEVEL</div>
            {[["Critical Sections", "critical", "var(--noncompliant)"], ["High Risk Sections", "high", "var(--atrisk)"], ["Medium Risk Sections", "medium", "var(--partial)"]].map(([label, risk, color]) => {
              const rs = scores.filter(s => s.section_risk_level === risk)
              const avg = rs.length > 0 ? rs.reduce((a, s) => a + parseFloat(s.percentage || 0), 0) / rs.length : 0
              return (
                <div key={risk} style={{ marginBottom: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}><span style={{ fontSize: 12, color: "var(--text2)" }}>{label}</span><span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color }}>{avg.toFixed(0)}%</span></div>
                  <ProgressBar value={avg} color={color} height={5} />
                </div>
              )
            })}
          </Card>
        </div>
      </div>

      <Tabs tabs={[["overview", "Overview"], ["sections", `Sections (${scores.length})`], ["gaps", `Gaps (${gaps.length})`]]} active={tab} onChange={setTab} />

      {tab === "overview" && (
        <div className="fade-up" style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          <StatCard label="Total Sections" value={scores.length} color="var(--blue)" />
          <StatCard label="Non-Compliant" value={noGaps.length} color="var(--noncompliant)" />
          <StatCard label="Partial" value={partGaps.length} color="var(--partial)" />
          <StatCard label="Score" value={Math.round(assessment?.overall_score || 0)} unit="/ 1000" color="var(--gold)" />
        </div>
      )}

      {tab === "sections" && (
        <Card className="fade-up">
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 480, overflowY: "auto" }}>
            {scores.map(sc => {
              const p = parseFloat(sc.percentage || 0)
              const color = p >= 80 ? "var(--compliant)" : p >= 60 ? "var(--partial)" : p >= 40 ? "var(--atrisk)" : "var(--noncompliant)"
              return (
                <div key={sc.id || sc.section} style={{ display: "grid", gridTemplateColumns: "26px 1fr 90px 56px 54px", gap: 10, alignItems: "center", padding: "9px 10px", borderRadius: "var(--radius)", background: "var(--bg3)" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text3)" }}>{sc.section_number}</span>
                  <div><div style={{ fontSize: 11, color: "var(--text)", marginBottom: 3 }}>{sc.section_title}</div><ProgressBar value={p} height={4} /></div>
                  <Badge color={sc.section_risk_level === "critical" ? "var(--noncompliant)" : sc.section_risk_level === "high" ? "var(--atrisk)" : sc.section_risk_level === "medium" ? "var(--partial)" : "var(--compliant)"}>{sc.section_risk_level}</Badge>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color, textAlign: "right", fontWeight: 700 }}>{p.toFixed(0)}%</div>
                  <div style={{ textAlign: "right", fontFamily: "var(--font-mono)", fontSize: 10, color: (sc.gap_count || 0) > 0 ? "var(--noncompliant)" : "var(--compliant)" }}>{(sc.gap_count || 0) > 0 ? `${sc.gap_count}g` : "✓"}</div>
                </div>
              )
            })}
          </div>
        </Card>
      )}

      {tab === "gaps" && (
        <Card className="fade-up">
          {gaps.length === 0 ? <div style={{ textAlign: "center", padding: "40px 0", color: "var(--compliant)", fontSize: 14 }}>✓ No gaps identified — fully compliant</div> :
            <div style={{ display: "flex", flexDirection: "column", gap: 9, maxHeight: 500, overflowY: "auto" }}>
              {gaps.map((gap, i) => {
                const isNo = gap.answer === "no"
                const color = isNo ? "var(--noncompliant)" : "var(--partial)"
                const riskColor = gap.section_risk_level === "critical" ? "var(--noncompliant)" : gap.section_risk_level === "high" ? "var(--atrisk)" : "var(--partial)"
                return (
                  <div key={i} style={{ padding: "11px 14px", borderRadius: "var(--radius)", background: "var(--bg3)", borderLeft: `3px solid ${color}` }}>
                    <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text3)", flexShrink: 0, paddingTop: 2, width: 38 }}>{gap.section_number}.{gap.question_number}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, color: "var(--text)", lineHeight: 1.5, marginBottom: 7 }}>{gap.question_text}</div>
                        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
                          <Badge color={riskColor}>{gap.section_risk_level}</Badge>
                          <Badge color={color}>{isNo ? "Non-Compliant" : "Partial"}</Badge>
                          <span style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{gap.section_title}</span>
                          <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--noncompliant)", fontFamily: "var(--font-mono)" }}>-{parseFloat(gap.points_lost || 0).toFixed(0)}pts</span>
                        </div>
                        {gap.notes && <div style={{ marginTop: 5, fontSize: 11, color: "var(--text3)", fontStyle: "italic" }}>Note: {gap.notes}</div>}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>}
        </Card>
      )}
    </AppShell>
  )
}

// Reports
function Reports() {
  const nav = useNavigate()
  const { toast } = useToast()
  const [assessments, setAssessments] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(null)

  useEffect(() => { api.get("/assessments/").then(({ data }) => { const all = data.results || data; setAssessments(all.filter(a => a.status === "completed")) }).catch(console.error).finally(() => setLoading(false)) }, [])

  const downloadPDF = async a => {
    setDownloading(a.id)
    try {
      const token = localStorage.getItem("axiomgh_token")
      const res = await fetch(`http://localhost:8000/api/v1/assessments/${a.id}/pdf_report/`, { headers: { Authorization: `Bearer ${token}` } })
      if (!res.ok) throw new Error()
      const blob = await res.blob(); const url = window.URL.createObjectURL(blob)
      const el = document.createElement("a"); el.href = url
      el.download = `AxiomGH_CISD2026_${a.institution_name?.replace(/\s/g, "_")}_${new Date(a.completed_at).toISOString().split("T")[0]}.pdf`
      el.click(); window.URL.revokeObjectURL(url)
      toast("PDF downloaded", "success")
    } catch { toast("Download failed", "error") }
    finally { setDownloading(null) }
  }

  return (
    <AppShell>
      <PageHeader label="REPORTS" title="Compliance Reports" subtitle="Download PDF reports for completed assessments" />
      {loading ? <div style={{ display: "flex", justifyContent: "center", paddingTop: 60 }}><Spinner size={28} /></div> :
        assessments.length === 0 ? <EmptyState icon="▤" title="No Reports Available" desc="Complete an assessment to generate your first compliance report." action={() => nav("/assessments/new")} actionLabel="Start Assessment" /> :
        <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {assessments.map(a => {
            const pct = parseFloat(a.overall_percentage || 0)
            const rating = pct >= 80 ? "compliant" : pct >= 60 ? "partial" : pct >= 40 ? "at_risk" : "non_compliant"
            return (
              <Card key={a.id} style={{ padding: "18px 22px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
                    <div style={{ width: 42, height: 42, borderRadius: "var(--radius)", background: "var(--bg3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, color: "var(--text3)" }}>▤</div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 4 }}>CISD 2026 Report — {a.institution_name}</div>
                      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <RatingBadge rating={rating} />
                        <span style={{ fontSize: 11, color: "var(--text3)" }}>{new Date(a.completed_at).toLocaleDateString("en-GH", { day: "numeric", month: "short", year: "numeric" })}</span>
                        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--gold)" }}>{Math.round(a.overall_score || 0)}/1000</span>
                      </div>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <Btn variant="ghost" size="sm" onClick={() => nav(`/assessments/${a.id}/results`)}>View Results</Btn>
                    <Btn size="sm" onClick={() => downloadPDF(a)} disabled={downloading === a.id}>{downloading === a.id ? <><Spinner size={13} /> Generating...</> : "↓ Download PDF"}</Btn>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>}
    </AppShell>
  )
}

// Benchmarks
function Benchmarks() {
  const [type, setType] = useState("commercial_bank")
  const [data, setData] = useState([])
  const [myScores, setMyScores] = useState({})
  const [loading, setLoading] = useState(false)

  const TYPES = [["commercial_bank", "Commercial Banks"], ["fintech", "Fintechs"], ["payment_processor", "Payment Processors"], ["savings_bank", "Savings & Loans"], ["microfinance", "Microfinance"]]

  useEffect(() => {
    setLoading(true)
    Promise.all([api.get(`/benchmarks/?type=${type}`).catch(() => ({ data: [] })), api.get("/assessments/").catch(() => ({ data: [] }))]).then(async ([{ data: bd }, { data: ad }]) => {
      setData(bd.results || bd)
      const all = ad.results || ad
      const latest = all.find(a => a.status === "completed")
      if (latest) { try { const { data: sc } = await api.get(`/assessments/${latest.id}/scores/`); const map = {}; sc.forEach(s => { map[s.section_number] = parseFloat(s.percentage || 0) }); setMyScores(map) } catch {} }
    }).finally(() => setLoading(false))
  }, [type])

  return (
    <AppShell>
      <PageHeader label="BENCHMARKING" title="Industry Benchmarks" subtitle="Compare your scores against anonymised peer institutions" />
      <div className="fade-up" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
        {TYPES.map(([val, label]) => <button key={val} onClick={() => setType(val)} style={{ padding: "7px 14px", borderRadius: "var(--radius)", border: `1px solid ${type === val ? "var(--gold)" : "var(--border)"}`, background: type === val ? "rgba(240,180,41,0.08)" : "var(--bg3)", color: type === val ? "var(--gold)" : "var(--text3)", fontSize: 12, fontWeight: type === val ? 600 : 400, cursor: "pointer" }}>{label}</button>)}
      </div>
      {loading ? <div style={{ display: "flex", justifyContent: "center", paddingTop: 60 }}><Spinner size={28} /></div> :
        data.length === 0 ? <EmptyState icon="◎" title="No Benchmark Data Yet" desc="Benchmark data populates as more institutions complete assessments. Complete your first assessment to contribute." /> :
        <Card className="fade-up-1">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
            <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em" }}>{TYPES.find(t => t[0] === type)?.[1]?.toUpperCase()} — {data[0]?.sample_size || 0} INSTITUTIONS</div>
            <div style={{ display: "flex", gap: 10 }}>
              {[["var(--blue)", "Peer Avg"], ["var(--text3)", "Median"], ["var(--compliant)", "Top 25%"], ["var(--gold)", "Your Score"]].map(([color, label]) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: color }} />
                  <span style={{ fontSize: 9, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {data.map(b => {
              const sectionNum = b.section_title?.match(/\d+/)?.[0]
              const mine = myScores[sectionNum] !== undefined ? myScores[sectionNum] : null
              const vs = mine !== null ? mine - parseFloat(b.avg_score) : null
              return (
                <div key={b.section} style={{ display: "grid", gridTemplateColumns: "26px 1fr 54px 54px 54px 64px", gap: 10, alignItems: "center", padding: "8px 10px", borderRadius: "var(--radius)", background: "var(--bg3)" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--text3)" }}>{sectionNum}</span>
                  <div><div style={{ fontSize: 11, color: "var(--text)", marginBottom: 4 }}>{b.section_title}</div><ProgressBar value={parseFloat(b.avg_score)} color="var(--blue)" height={4} /></div>
                  {[["var(--blue)", parseFloat(b.avg_score)], ["var(--text2)", parseFloat(b.median_score)], ["var(--compliant)", parseFloat(b.top_quartile_score)]].map(([color, val], ci) => (
                    <div key={ci} style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 8, color: "var(--text3)", fontFamily: "var(--font-mono)", marginBottom: 2 }}>{["AVG", "MED", "TOP"][ci]}</div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color, fontWeight: 600 }}>{val.toFixed(0)}%</div>
                    </div>
                  ))}
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 8, color: "var(--text3)", fontFamily: "var(--font-mono)", marginBottom: 2 }}>YOURS</div>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: mine !== null ? "var(--gold)" : "var(--text3)", fontWeight: mine !== null ? 700 : 400 }}>
                      {mine !== null ? `${mine.toFixed(0)}%` : "—"}
                    </div>
                    {vs !== null && <div style={{ fontSize: 8, color: vs >= 0 ? "var(--compliant)" : "var(--noncompliant)", fontFamily: "var(--font-mono)" }}>{vs >= 0 ? "+" : ""}{vs.toFixed(0)}%</div>}
                  </div>
                </div>
              )
            })}
          </div>
        </Card>}
    </AppShell>
  )
}

// Settings
function Settings() {
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const [tab, setTab] = useState("profile")
  const [profile, setProfile] = useState({ first_name: user?.first_name || "", last_name: user?.last_name || "", email: user?.email || "" })
  const [passwords, setPasswords] = useState({ current: "", new: "", confirm: "" })
  const [saving, setSaving] = useState(false)

  const saveProfile = async () => { setSaving(true); await new Promise(r => setTimeout(r, 700)); toast("Profile updated", "success"); setSaving(false) }
  const changePass = async () => {
    if (passwords.new !== passwords.confirm) { toast("Passwords do not match", "error"); return }
    if (passwords.new.length < 8) { toast("Password must be at least 8 characters", "error"); return }
    setSaving(true); await new Promise(r => setTimeout(r, 700)); toast("Password changed", "success"); setPasswords({ current: "", new: "", confirm: "" }); setSaving(false)
  }

  return (
    <AppShell>
      <PageHeader label="SETTINGS" title="Account Settings" />
      <Tabs tabs={[["profile", "Profile"], ["security", "Security"], ["about", "About"]]} active={tab} onChange={setTab} />
      <div style={{ maxWidth: 520 }}>
        {tab === "profile" && (
          <Card className="fade-up">
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 18 }}>Profile Information</div>
            <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 24 }}>
              <div style={{ width: 56, height: 56, borderRadius: "50%", background: "var(--gold)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 20, color: "#080C12", flexShrink: 0 }}>{profile.first_name?.[0]}{profile.last_name?.[0]}</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>{profile.first_name} {profile.last_name}</div>
                <div style={{ fontSize: 11, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{user?.role?.toUpperCase()}</div>
                <div style={{ fontSize: 11, color: "var(--text3)" }}>{user?.institution_name}</div>
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {[["FIRST NAME", "first_name"], ["LAST NAME", "last_name"]].map(([label, key]) => (
                  <div key={key}><label style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", display: "block", marginBottom: 5 }}>{label}</label><input value={profile[key]} onChange={e => setProfile(p => ({ ...p, [key]: e.target.value }))} /></div>
                ))}
              </div>
              <div><label style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", display: "block", marginBottom: 5 }}>EMAIL ADDRESS</label><input type="email" value={profile.email} onChange={e => setProfile(p => ({ ...p, email: e.target.value }))} /></div>
              <Btn onClick={saveProfile} disabled={saving} style={{ alignSelf: "flex-start" }}>{saving ? <><Spinner size={13} /> Saving...</> : "Save Changes"}</Btn>
            </div>
          </Card>
        )}

        {tab === "security" && (
          <Card className="fade-up">
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 18 }}>Change Password</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {[["CURRENT PASSWORD", "current"], ["NEW PASSWORD", "new"], ["CONFIRM NEW PASSWORD", "confirm"]].map(([label, key]) => (
                <div key={key}><label style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", display: "block", marginBottom: 5 }}>{label}</label><input type="password" value={passwords[key]} onChange={e => setPasswords(p => ({ ...p, [key]: e.target.value }))} placeholder="••••••••" /></div>
              ))}
              <div style={{ padding: "10px 12px", background: "rgba(240,180,41,0.04)", borderRadius: "var(--radius)", border: "1px solid rgba(240,180,41,0.12)" }}>
                <div style={{ fontSize: 10, color: "var(--gold)", fontFamily: "var(--font-mono)", marginBottom: 5 }}>REQUIREMENTS</div>
                <div style={{ fontSize: 11, color: "var(--text3)", lineHeight: 1.7 }}>• Minimum 8 characters<br/>• Mix of letters and numbers recommended</div>
              </div>
              <Btn onClick={changePass} disabled={saving || !passwords.current || !passwords.new} style={{ alignSelf: "flex-start" }}>{saving ? <><Spinner size={13} /> Updating...</> : "Change Password"}</Btn>
            </div>
          </Card>
        )}

        {tab === "about" && (
          <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <Card>
              <div style={{ fontSize: 10, color: "var(--text3)", fontFamily: "var(--font-mono)", letterSpacing: "0.1em", marginBottom: 14 }}>PLATFORM INFORMATION</div>
              {[["Platform", "AxiomGH Compliance Intelligence"], ["Version", "1.0.0"], ["Directive", "BoG CISD 2026"], ["Sections", "23 (including 3 new 2026 sections)"], ["Questions", "172 assessment questions"], ["Scoring", "Weighted score out of 1000"], ["Built for", "Ghana Regulated Financial Institutions"]].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                  <span style={{ fontSize: 12, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{k}</span>
                  <span style={{ fontSize: 12, color: "var(--text)" }}>{v}</span>
                </div>
              ))}
            </Card>
            <Card style={{ background: "rgba(240,180,41,0.03)", borderColor: "rgba(240,180,41,0.15)" }}>
              <div style={{ fontSize: 10, color: "var(--gold)", fontFamily: "var(--font-mono)", marginBottom: 8 }}>LEGAL DISCLAIMER</div>
              <p style={{ fontSize: 12, color: "var(--text2)", lineHeight: 1.7 }}>AxiomGH assists regulated financial institutions in Ghana with self-assessment against the BoG CISD 2026. This does not constitute legal or regulatory advice. Institutions remain solely responsible for their compliance obligations.</p>
            </Card>
            <Btn variant="danger" size="sm" onClick={logout} style={{ alignSelf: "flex-start" }}>Sign Out of AxiomGH</Btn>
          </div>
        )}
      </div>
    </AppShell>
  )
}

// Protected Route
function Protected({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

// App
export default function App() {
  return (
    <>
      <style>{styles}</style>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/dashboard"               element={<Protected><Dashboard /></Protected>} />
              <Route path="/assessments"             element={<Protected><AssessmentsList /></Protected>} />
              <Route path="/assessments/new"         element={<Protected><NewAssessment /></Protected>} />
              <Route path="/assessments/:id"         element={<Protected><AssessmentFlow /></Protected>} />
              <Route path="/assessments/:id/results" element={<Protected><Results /></Protected>} />
              <Route path="/reports"                 element={<Protected><Reports /></Protected>} />
              <Route path="/benchmarks"              element={<Protected><Benchmarks /></Protected>} />
              <Route path="/settings"                element={<Protected><Settings /></Protected>} />
              <Route path="*"                        element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </>
  )
}
