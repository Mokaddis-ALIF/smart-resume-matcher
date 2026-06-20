import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Resumes from "./pages/Resumes";
import Results from "./pages/Results";
import Evaluation from "./pages/Evaluation";
import "./App.css";

function Sidebar() {
  const links = [
    { to: "/", label: "Dashboard", icon: "📊" },
    { to: "/jobs", label: "Jobs", icon: "💼" },
    { to: "/resumes", label: "Resumes", icon: "📄" },
    { to: "/results", label: "Results", icon: "✅" },
    { to: "/evaluation", label: "Evaluation", icon: "📈" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>ResumeAI</h1>
        <span className="sidebar-subtitle">Smart Resume Matcher</span>
      </div>
      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `nav-link ${isActive ? "nav-link-active" : ""}`
            }
          >
            <span className="nav-icon">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>
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
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/resumes" element={<Resumes />} />
            <Route path="/results" element={<Results />} />
            <Route path="/evaluation" element={<Evaluation />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
