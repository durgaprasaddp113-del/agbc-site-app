/* eslint-disable */
// Login.js — AGBC Site Management System
import { useState } from "react";
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://awzxxzaspmwqgrywplnu.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3enh4emFzcG13cWdyeXdwbG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY5MjI0NjgsImV4cCI6MjA5MjQ5ODQ2OH0._1uvuSwKvWCKUxilJuC-AiO9U2-rKz6yB6-MPrzwYxg";
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const USER_ROLES = [
  "Super Admin","Admin","Project Manager","Planning Engineer",
  "Site Engineer","QA/QC Engineer","QS Engineer","MEP Coordinator",
  "Procurement Engineer","Store Keeper","Safety Officer","Foreman",
  "Document Controller","Accountant","Site Supervisor",
  "Client Representative","Consultant Representative",
  "Subcontractor User","Read-Only User","Other",
];

const Inp = ({ label, type = "text", value, onChange, placeholder, required, autoComplete }) => (
  <div>
    <label className="block text-xs font-bold text-slate-600 mb-1">
      {label}{required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
    <input
      type={type} value={value} onChange={onChange}
      placeholder={placeholder || ""} autoComplete={autoComplete}
      className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 bg-white transition-colors"
    />
  </div>
);

const Sel = ({ label, value, onChange, children, required }) => (
  <div>
    <label className="block text-xs font-bold text-slate-600 mb-1">
      {label}{required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
    <select
      value={value} onChange={onChange}
      className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 bg-white transition-colors"
    >
      {children}
    </select>
  </div>
);

const PasswordStrength = ({ password }) => {
  if (!password) return null;
  const score = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ].filter(Boolean).length;
  const colors = ["", "bg-red-400", "bg-amber-400", "bg-blue-500", "bg-green-500"];
  const labels = ["", "Weak", "Fair", "Strong", "Very Strong"];
  return (
    <div className="mt-1.5">
      <div className="flex gap-1 mb-0.5">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className={`flex-1 h-1 rounded-full ${i <= score ? colors[score] : "bg-slate-200"}`} />
        ))}
      </div>
      <p className={`text-xs font-semibold ${score < 2 ? "text-red-500" : score < 3 ? "text-amber-500" : score < 4 ? "text-blue-500" : "text-green-600"}`}>
        {labels[score]}
      </p>
    </div>
  );
};

const Spinner = () => (
  <span className="flex items-center justify-center gap-2">
    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  </span>
);

export default function Login({ onLogin }) {
  const [view, setView]       = useState("signin");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [errType, setErrType] = useState("error");
  const [showPw, setShowPw]   = useState(false);
  const [showCPw, setShowCPw] = useState(false);

  const [email, setEmail]     = useState("");
  const [password, setPassword] = useState("");

  const EMPTY_SU = {
    fullName: "", email: "", mobile: "", company: "",
    role: "Site Engineer", department: "",
    password: "", confirmPw: "", remarks: "",
  };
  const [su, setSu] = useState(EMPTY_SU);
  const sf = k => e => setSu(p => ({ ...p, [k]: e.target.value }));

  const setErr = (msg, type = "error") => { setError(msg); setErrType(type); };
  const clearErr = () => setError("");
  const goSignIn = () => { clearErr(); setSu(EMPTY_SU); setView("signin"); };
  const goSignUp = () => { clearErr(); setView("signup"); };

  // ── SIGN IN — no approval check ──────────────────────────────────────────
  const handleSignIn = async (e) => {
    e.preventDefault(); clearErr(); setLoading(true);
    const { data, error: authErr } = await supabase.auth.signInWithPassword({
      email: email.trim(), password,
    });
    if (authErr) {
      setErr(
        authErr.message.includes("Invalid")
          ? "Incorrect email or password. Please try again."
          : authErr.message
      );
      setLoading(false); return;
    }
    setLoading(false);
    if (onLogin) onLogin(data.user);
  };

  // ── SIGN UP — creates user as Active, no approval needed ─────────────────
  const handleSignUp = async (e) => {
    e.preventDefault(); clearErr();
    if (!su.fullName.trim())  { setErr("Full name is required."); return; }
    if (!su.email.trim())     { setErr("Email address is required."); return; }
    if (!/\S+@\S+\.\S+/.test(su.email)) { setErr("Please enter a valid email address."); return; }
    if (!su.mobile.trim())    { setErr("Mobile number is required."); return; }
    if (!su.company.trim())   { setErr("Company name is required."); return; }
    if (!su.role)             { setErr("Please select a role."); return; }
    if (su.password.length < 6) { setErr("Password must be at least 6 characters."); return; }
    if (su.password !== su.confirmPw) { setErr("Passwords do not match."); return; }

    setLoading(true);

    const { data, error: authErr } = await supabase.auth.signUp({
      email: su.email.trim().toLowerCase(),
      password: su.password,
      options: { data: { full_name: su.fullName.trim() } },
    });

    if (authErr) {
      setErr(
        authErr.message.includes("already")
          ? "This email is already registered. Please sign in instead."
          : authErr.message
      );
      setLoading(false); return;
    }

    // Save profile as Active — no approval required
    await supabase.from("users").insert([{
      email:        su.email.trim().toLowerCase(),
      full_name:    su.fullName.trim(),
      phone:        su.mobile.trim(),
      mobile:       su.mobile.trim(),
      company_name: su.company.trim(),
      role:         su.role,
      department:   su.department.trim(),
      status:       "Active",
      is_active:    true,
      notes:        `Role: ${su.role}${su.department ? ` | Dept: ${su.department}` : ""}${su.remarks ? ` | ${su.remarks}` : ""}`,
    }]);

    setLoading(false);
    // Sign them in directly
    const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({
      email: su.email.trim().toLowerCase(), password: su.password,
    });
    if (!signInErr && signInData && onLogin) onLogin(signInData.user);
    else setView("signin"); // fallback: go to sign in
  };

  const Alert = ({ msg, type }) => {
    const s = {
      error:   "bg-red-50 border-red-200 text-red-700",
      warning: "bg-amber-50 border-amber-200 text-amber-800",
      info:    "bg-blue-50 border-blue-200 text-blue-700",
      success: "bg-green-50 border-green-200 text-green-700",
    };
    const ic = { error: "⚠️", warning: "⏳", info: "ℹ️", success: "✅" };
    return (
      <div className={`border rounded-xl px-4 py-3 mb-4 flex items-start gap-2 text-xs font-semibold ${s[type]}`}>
        <span className="text-sm mt-0.5 shrink-0">{ic[type]}</span>
        <span className="leading-relaxed">{msg}</span>
      </div>
    );
  };

  const PwField = ({ label, value, onChange, show, onToggle, placeholder, checkMatch, matchValue }) => (
    <div>
      <label className="block text-xs font-bold text-slate-600 mb-1">
        {label} <span className="text-red-500">*</span>
      </label>
      <div className="relative">
        <input
          type={show ? "text" : "password"} value={value} onChange={onChange}
          placeholder={placeholder}
          className={`w-full border rounded-xl px-3 py-2.5 pr-10 text-sm text-slate-800 outline-none focus:ring-2 bg-white transition-colors
            ${checkMatch && value
              ? value === matchValue
                ? "border-green-300 focus:border-green-400 focus:ring-green-100"
                : "border-red-300 focus:border-red-400 focus:ring-red-100"
              : "border-slate-200 focus:border-amber-400 focus:ring-amber-100"
            }`}
        />
        <button type="button" onClick={onToggle} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">
          {show ? "🙈" : "👁️"}
        </button>
      </div>
      {checkMatch && value && value !== matchValue && (
        <p className="text-xs text-red-500 mt-1 font-semibold">Passwords do not match</p>
      )}
      {checkMatch && value && value === matchValue && (
        <p className="text-xs text-green-600 mt-1 font-semibold">✓ Passwords match</p>
      )}
    </div>
  );

  const Header = () => (
    <div className="text-center mb-6">
      <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-lg mb-3">
        <span className="text-amber-400 text-2xl font-black">AG</span>
      </div>
      <h1 className="text-xl font-black text-slate-800">Al Ghaith Building</h1>
      <p className="text-xs text-slate-500 mt-0.5">Construction Co. LLC — Site Management System</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center p-4">
      <div className={`bg-white rounded-2xl shadow-xl w-full overflow-x-hidden transition-all ${view === "signup" ? "max-w-lg" : "max-w-md"}`}>
        <div className="h-1.5 bg-gradient-to-r from-amber-400 via-amber-500 to-amber-400" />
        <div className="p-8">
          <Header />

          {/* Tab Toggle */}
          <div className="flex rounded-xl bg-slate-100 p-1 mb-6">
            {[["signin", "🔐 Sign In"], ["signup", "📝 Sign Up"]].map(([v, l]) => (
              <button key={v} onClick={() => { clearErr(); setView(v); }}
                className={`flex-1 py-2 rounded-lg text-sm font-bold transition-colors ${view === v ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}>
                {l}
              </button>
            ))}
          </div>

          {error && <Alert msg={error} type={errType} />}

          {/* ── SIGN IN ── */}
          {view === "signin" && (
            <form onSubmit={handleSignIn} className="space-y-4">
              <Inp label="Email Address" type="email" value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="your@email.com" required autoComplete="email" />
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">
                  Password <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showPw ? "text" : "password"} value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••" autoComplete="current-password"
                    className="w-full border border-slate-200 rounded-xl px-3 py-2.5 pr-10 text-sm text-slate-800 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 bg-white"
                  />
                  <button type="button" onClick={() => setShowPw(p => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">
                    {showPw ? "🙈" : "👁️"}
                  </button>
                </div>
              </div>
              <button type="submit" disabled={loading}
                className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold py-3 rounded-xl text-sm shadow-sm transition-all disabled:opacity-60">
                {loading ? <><Spinner /> Signing in...</> : "Sign In →"}
              </button>
              <p className="text-center text-xs text-slate-400">
                Don't have an account?{" "}
                <button type="button" onClick={goSignUp} className="text-amber-600 font-bold hover:underline">
                  Create Account
                </button>
              </p>
            </form>
          )}

          {/* ── SIGN UP ── */}
          {view === "signup" && (
            <form onSubmit={handleSignUp} className="space-y-3">

              {/* Personal Info */}
              <div className="bg-slate-50 rounded-xl p-3 space-y-3 border border-slate-100">
                <div className="text-xs font-black text-slate-400 uppercase tracking-widest">👤 Personal Information</div>
                <Inp label="Full Name" value={su.fullName} onChange={sf("fullName")}
                  placeholder="Eng. Ahmed Al Mansoori" required />
                <Inp label="Email Address" type="email" value={su.email} onChange={sf("email")}
                  placeholder="your@email.com" required autoComplete="email" />
                <Inp label="Mobile Number" type="tel" value={su.mobile} onChange={sf("mobile")}
                  placeholder="+971 50 XXX XXXX" required />
              </div>

              {/* Company Details */}
              <div className="bg-slate-50 rounded-xl p-3 space-y-3 border border-slate-100">
                <div className="text-xs font-black text-slate-400 uppercase tracking-widest">🏢 Company Details</div>
                <Inp label="Company Name" value={su.company} onChange={sf("company")}
                  placeholder="Al Ghaith Building Construction Co. LLC" required />
                <div className="grid grid-cols-2 gap-3">
                  {/* SINGLE FIELD — Role only, no duplicate designation */}
                  <Sel label="Role" value={su.role} onChange={sf("role")} required>
                    {USER_ROLES.map(r => <option key={r}>{r}</option>)}
                  </Sel>
                  <Inp label="Department" value={su.department} onChange={sf("department")}
                    placeholder="Civil / MEP / Admin" />
                </div>
              </div>

              {/* Password */}
              <div className="bg-slate-50 rounded-xl p-3 space-y-3 border border-slate-100">
                <div className="text-xs font-black text-slate-400 uppercase tracking-widest">🔐 Set Password</div>
                <div>
                  <PwField label="Password" value={su.password} onChange={sf("password")}
                    show={showPw} onToggle={() => setShowPw(p => !p)}
                    placeholder="Minimum 6 characters" />
                  <PasswordStrength password={su.password} />
                </div>
                <PwField label="Confirm Password" value={su.confirmPw} onChange={sf("confirmPw")}
                  show={showCPw} onToggle={() => setShowCPw(p => !p)}
                  placeholder="Repeat password" checkMatch matchValue={su.password} />
              </div>

              {/* Remarks */}
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">
                  Additional Remarks (Optional)
                </label>
                <textarea value={su.remarks} onChange={sf("remarks")} rows={2}
                  placeholder="Any additional information..."
                  className="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 bg-white resize-none" />
              </div>

              <button type="submit" disabled={loading}
                className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold py-3 rounded-xl text-sm shadow-sm transition-all disabled:opacity-60">
                {loading ? <><Spinner /> Creating account...</> : "Create Account →"}
              </button>
              <p className="text-center text-xs text-slate-400">
                Already have an account?{" "}
                <button type="button" onClick={goSignIn} className="text-amber-600 font-bold hover:underline">
                  Sign In
                </button>
              </p>
            </form>
          )}
        </div>
        <div className="px-8 pb-5 text-center text-xs text-slate-300">
          © {new Date().getFullYear()} Al Ghaith Building Construction Co. LLC
        </div>
      </div>
    </div>
  );
}