import { useState, useEffect } from "react";
import { getTaxonomy, addTaxonomySkill, updateTaxonomySkill, deleteTaxonomySkill, getTaxonomyCategories } from "../services/api";

const catColors = {
  language: { bg: "#eef2ff", text: "#4338ca" },
  framework: { bg: "#f0fdf4", text: "#166534" },
  database: { bg: "#fef3c7", text: "#92400e" },
  cloud: { bg: "#eff6ff", text: "#1e40af" },
  devops: { bg: "#fce7f3", text: "#9d174d" },
  tool: { bg: "#f3f4f6", text: "#374151" },
  ml: { bg: "#faf5ff", text: "#7c3aed" },
  mobile: { bg: "#ecfdf5", text: "#047857" },
  testing: { bg: "#fff7ed", text: "#c2410c" },
  messaging: { bg: "#fdf2f8", text: "#be185d" },
  methodology: { bg: "#f0f9ff", text: "#0369a1" },
};

export default function Taxonomy() {
  const [skills, setSkills] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filterCat, setFilterCat] = useState("");
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);
  const [form, setForm] = useState({ name: "", category: "tool", aliases: "" });

  const fetchData = async () => {
    try {
      const data = await getTaxonomy();
      setSkills(data.skills);
      const cats = await getTaxonomyCategories();
      setCategories(cats.categories);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const filtered = skills.filter(s => {
    if (filterCat && s.category !== filterCat) return false;
    if (search && !s.name.toLowerCase().includes(search.toLowerCase()) &&
        !s.aliases.some(a => a.toLowerCase().includes(search.toLowerCase()))) return false;
    return true;
  });

  const grouped = {};
  filtered.forEach(s => {
    if (!grouped[s.category]) grouped[s.category] = [];
    grouped[s.category].push(s);
  });

  const openAdd = () => {
    setEditingSkill(null);
    setForm({ name: "", category: "tool", aliases: "" });
    setShowAdd(true);
  };

  const openEdit = (skill) => {
    setEditingSkill(skill);
    setForm({ name: skill.name, category: skill.category, aliases: skill.aliases.join(", ") });
    setShowAdd(true);
  };

  const closeForm = () => {
    setShowAdd(false);
    setEditingSkill(null);
    setForm({ name: "", category: "tool", aliases: "" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const aliases = form.aliases.split(",").map(a => a.trim()).filter(Boolean);
    try {
      if (editingSkill) {
        await updateTaxonomySkill(editingSkill.id, form.name, form.category, aliases);
      } else {
        await addTaxonomySkill(form.name, form.category, aliases);
      }
      closeForm();
      fetchData();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDelete = async (skill) => {
    if (!window.confirm(`Delete "${skill.name}" from the taxonomy?`)) return;
    try {
      await deleteTaxonomySkill(skill.id);
      fetchData();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Skill Taxonomy</h2>
          <p>Manage the skill database used for CV matching — {skills.length} skills across {categories.length} categories</p>
        </div>
        <button className="btn btn-primary" onClick={showAdd ? closeForm : openAdd}>
          {showAdd ? "Cancel" : "+ Add Skill"}
        </button>
      </div>

      {/* Add/Edit form */}
      {showAdd && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
            {editingSkill ? `Edit: ${editingSkill.name}` : "Add New Skill"}
          </h3>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={labelStyle}>Skill Name *</label>
                <input style={inputStyle} required value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Deno" />
              </div>
              <div>
                <label style={labelStyle}>Category *</label>
                <select style={inputStyle} value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                  {categories.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label style={labelStyle}>Aliases (comma separated)</label>
              <input style={inputStyle} value={form.aliases} onChange={e => setForm({...form, aliases: e.target.value})} placeholder="e.g. deno, deno.js, deno runtime" />
              <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 4 }}>
                These are alternative names that will also match this skill in CVs
              </div>
            </div>
            <div>
              <button className="btn btn-primary" type="submit">{editingSkill ? "Save Changes" : "Add Skill"}</button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <input
          style={{ ...inputStyle, flex: 1 }}
          placeholder="Search skills or aliases..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          style={{ ...inputStyle, width: 160 }}
          value={filterCat}
          onChange={e => setFilterCat(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map(c => (
            <option key={c} value={c}>{c} ({skills.filter(s => s.category === c).length})</option>
          ))}
        </select>
      </div>

      {/* Skills by category */}
      {Object.entries(grouped).sort().map(([cat, catSkills]) => {
        const colors = catColors[cat] || { bg: "#f3f4f6", text: "#374151" };
        return (
          <div key={cat} className="card" style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <h3 style={{
                fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em",
                color: colors.text, display: "flex", alignItems: "center", gap: 6,
              }}>
                <span style={{ padding: "2px 8px", borderRadius: 6, background: colors.bg, fontSize: 11 }}>{cat}</span>
                {catSkills.length} skills
              </h3>
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {catSkills.map(skill => (
                <div
                  key={skill.id}
                  style={{
                    fontSize: 12, padding: "5px 12px", borderRadius: 8,
                    background: colors.bg, color: colors.text,
                    border: `1px solid ${colors.bg}`,
                    display: "flex", alignItems: "center", gap: 6, cursor: "pointer",
                  }}
                  onClick={() => openEdit(skill)}
                  title={`Aliases: ${skill.aliases.join(", ")}\nClick to edit`}
                >
                  {skill.name}
                  <span
                    onClick={e => { e.stopPropagation(); handleDelete(skill); }}
                    style={{ fontSize: 10, color: "#dc2626", cursor: "pointer", opacity: 0.5 }}
                    title="Delete"
                  >✕</span>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {filtered.length === 0 && (
        <div className="card" style={{ textAlign: "center", padding: 30, color: "#9ca3af" }}>
          No skills found matching your search
        </div>
      )}
    </div>
  );
}

const labelStyle = { display: "block", fontSize: 13, fontWeight: 500, color: "#374151", marginBottom: 4 };
const inputStyle = { width: "100%", padding: "8px 12px", borderRadius: 6, border: "1px solid #d1d5db", fontSize: 14, fontFamily: "inherit", outline: "none" };
