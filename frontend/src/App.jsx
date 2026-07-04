import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Resumes from "./pages/Resumes";
import Results from "./pages/Results";
import Evaluation from "./pages/Evaluation";
import Taxonomy from "./pages/Taxonomy";
import "./App.css";

const NAV_LINKS = [
  { to: "/",          label: "Dashboard",  icon: "📊", end: true },
  { to: "/jobs",      label: "Jobs",       icon: "💼" },
  { to: "/resumes",   label: "Resumes",    icon: "📄" },
  { to: "/results",   label: "Results",    icon: "🏆" },
  { to: "/evaluation",label: "Evaluation", icon: "📈" },
  { to: "/taxonomy",  label: "Taxonomy",   icon: "🏷️" },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🤖</div>
          <h1>ResumeAI</h1>
        </div>
        <span className="sidebar-subtitle">Smart Hiring Platform</span>
      </div>

      <div className="sidebar-section-label">Navigation</div>

      <nav className="sidebar-nav">
        {NAV_LINKS.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => `nav-link${isActive ? " nav-link-active" : ""}`}
          >
            <span className="nav-icon">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        Smart Resume Matcher v1.0
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/"           element={<Dashboard />} />
            <Route path="/jobs"       element={<Jobs />} />
            <Route path="/resumes"    element={<Resumes />} />
            <Route path="/results"    element={<Results />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="/taxonomy"   element={<Taxonomy />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
