import { useEffect, useState } from "react";

const emptyTemplate = { label: "", subject: "", body: "" };

function useConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then(setConfig)
      .catch(() => setError("Config konnte nicht geladen werden."))
      .finally(() => setLoading(false));
  }, []);

  return { config, setConfig, loading, error };
}

function TimesEditor({ times, onChange }) {
  const [newTime, setNewTime] = useState("");

  function addTime() {
    if (!/^([01]\d|2[0-3]):([0-5]\d)$/.test(newTime)) return;
    if (times.includes(newTime)) return;
    onChange([...times, newTime].sort());
    setNewTime("");
  }

  function removeTime(t) {
    onChange(times.filter((x) => x !== t));
  }

  return (
    <div className="card">
      <h2>Zeitplan</h2>
      <p className="hint">
        Uhrzeiten, zu denen die Recherche + E-Mail-Entwürfe laufen sollen. Nach dem Speichern bitte
        kurz Bescheid geben (oder committen/pushen), damit die zugehörigen Routinen synchron
        gehalten werden können.
      </p>
      <ul className="chip-list">
        {times.map((t) => (
          <li key={t} className="chip">
            {t}
            <button type="button" onClick={() => removeTime(t)} aria-label={`${t} entfernen`}>
              ×
            </button>
          </li>
        ))}
      </ul>
      <div className="row">
        <input
          type="time"
          value={newTime}
          onChange={(e) => setNewTime(e.target.value)}
        />
        <button type="button" onClick={addTime}>
          Zeit hinzufügen
        </button>
      </div>
    </div>
  );
}

function TemplateEditor({ title, template, onChange }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <label>
        Betreff
        <input
          type="text"
          value={template.subject}
          onChange={(e) => onChange({ ...template, subject: e.target.value })}
        />
      </label>
      <label>
        Text
        <textarea
          rows={8}
          value={template.body}
          onChange={(e) => onChange({ ...template, body: e.target.value })}
        />
      </label>
      <p className="hint">
        Platzhalter: <code>{"{{firma}}"}</code> <code>{"{{absender}}"}</code>{" "}
        <code>{"{{firmenname}}"}</code> <code>{"{{pdf_link}}"}</code>
      </p>
    </div>
  );
}

function PdfManager() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  function load() {
    fetch("/api/pdfs")
      .then((r) => r.json())
      .then(setFiles)
      .catch(() => setError("PDF-Liste konnte nicht geladen werden."));
  }

  useEffect(load, []);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError("");
    const formData = new FormData();
    formData.append("pdf", file);
    try {
      const res = await fetch("/api/pdfs", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Upload fehlgeschlagen.");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(filename) {
    setError("");
    try {
      const res = await fetch(`/api/pdfs/${encodeURIComponent(filename)}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Löschen fehlgeschlagen.");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>PDF-Anhänge</h2>
      <p className="hint">
        Alle hier hinterlegten PDFs werden bei der Ausführung zu Google Drive hochgeladen und als
        Link in jede E-Mail eingefügt (Gmail-Entwürfe unterstützen aktuell keine echten Anhänge).
        Datei löschen = wird nicht mehr verlinkt. Neue Datei hochladen = kommt zusätzlich dazu.
      </p>
      {error && <p className="error">{error}</p>}
      <input type="file" accept="application/pdf" onChange={handleUpload} disabled={uploading} />
      <ul className="file-list">
        {files.length === 0 && <li className="hint">Keine PDFs hinterlegt.</li>}
        {files.map((f) => (
          <li key={f.filename}>
            <span>{f.filename}</span>
            <span className="hint">{Math.round(f.sizeBytes / 1024)} KB</span>
            <button type="button" onClick={() => handleDelete(f.filename)}>
              Entfernen
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ContactedLog() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    fetch("/api/contacted")
      .then((r) => r.json())
      .then(setEntries)
      .catch(() => {});
  }, []);

  return (
    <div className="card">
      <h2>Bereits kontaktierte Firmen</h2>
      <p className="hint">Wird bei jedem Lauf aktualisiert, damit keine Firma doppelt angeschrieben wird.</p>
      {entries.length === 0 ? (
        <p className="hint">Noch keine Einträge.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Firma</th>
              <th>Domain</th>
              <th>Template</th>
              <th>Datum</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e, i) => (
              <tr key={i}>
                <td>{e.name}</td>
                <td>{e.domain || "–"}</td>
                <td>{e.template}</td>
                <td>{e.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function App() {
  const { config, setConfig, loading, error } = useConfig();
  const [saveState, setSaveState] = useState("");

  if (loading) return <p className="hint">Lade…</p>;
  if (error) return <p className="error">{error}</p>;
  if (!config) return null;

  async function save() {
    setSaveState("Speichere…");
    try {
      const res = await fetch("/api/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Speichern fehlgeschlagen.");
      setSaveState("Gespeichert. Bitte committen/pushen, damit Claude die Änderungen sieht.");
    } catch (err) {
      setSaveState(`Fehler: ${err.message}`);
    }
  }

  return (
    <main>
      <h1>Lorino Co. – E-Mail-Automatisierung</h1>
      <p className="hint">
        Konfiguration für die automatisierte Firmenrecherche und personalisierte E-Mail-Entwürfe.
        Entwürfe werden zur Freigabe in Gmail abgelegt, nichts wird ohne Prüfung versendet.
      </p>

      <div className="card">
        <h2>Zielgruppe</h2>
        <label>
          Firmenname (Absender)
          <input
            type="text"
            value={config.firmenname}
            onChange={(e) => setConfig({ ...config, firmenname: e.target.value })}
          />
        </label>
        <label>
          Branche
          <input
            type="text"
            value={config.targetIndustry}
            onChange={(e) => setConfig({ ...config, targetIndustry: e.target.value })}
          />
        </label>
        <label>
          Region
          <input
            type="text"
            value={config.targetRegion}
            onChange={(e) => setConfig({ ...config, targetRegion: e.target.value })}
          />
        </label>
        <label>
          Firmen pro Lauf
          <input
            type="number"
            min={1}
            max={50}
            value={config.companiesPerRun}
            onChange={(e) =>
              setConfig({ ...config, companiesPerRun: Number(e.target.value) })
            }
          />
        </label>
        <label>
          Google-Drive-Ordner für PDF-Links
          <input
            type="text"
            placeholder="https://drive.google.com/drive/folders/…"
            value={config.driveFolderUrl}
            onChange={(e) => setConfig({ ...config, driveFolderUrl: e.target.value })}
          />
        </label>
        <p className="hint">
          Einmalig einen Drive-Ordner anlegen und auf „Jeder mit dem Link – Betrachter“ freigeben.
          Neue PDF-Uploads werden in diesem Ordner abgelegt und erben die Freigabe, damit
          Empfänger den Link öffnen können.
        </p>
      </div>

      <TimesEditor
        times={config.times}
        onChange={(times) => setConfig({ ...config, times })}
      />

      <TemplateEditor
        title="Template A – mit Webseite"
        template={config.templateA}
        onChange={(templateA) => setConfig({ ...config, templateA })}
      />
      <TemplateEditor
        title="Template B – ohne Webseite"
        template={config.templateB}
        onChange={(templateB) => setConfig({ ...config, templateB })}
      />

      <PdfManager />
      <ContactedLog />

      <div className="card">
        <button type="button" onClick={save}>
          Konfiguration speichern
        </button>
        {saveState && <p className="hint">{saveState}</p>}
      </div>
    </main>
  );
}
