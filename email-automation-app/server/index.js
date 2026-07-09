import express from "express";
import cors from "cors";
import multer from "multer";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "data");
const PDF_DIR = path.join(DATA_DIR, "pdfs");
const CONFIG_PATH = path.join(DATA_DIR, "config.json");
const CONTACTED_PATH = path.join(DATA_DIR, "contacted.json");

fs.mkdirSync(PDF_DIR, { recursive: true });

const app = express();
app.use(cors());
app.use(express.json());

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return fallback;
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n");
}

const TIME_RE = /^([01]\d|2[0-3]):([0-5]\d)$/;

function validateConfig(body) {
  if (typeof body !== "object" || body === null) return "Config muss ein Objekt sein.";
  if (typeof body.firmenname !== "string" || !body.firmenname.trim()) return "firmenname fehlt.";
  if (typeof body.targetIndustry !== "string" || !body.targetIndustry.trim()) return "targetIndustry fehlt.";
  if (typeof body.targetRegion !== "string" || !body.targetRegion.trim()) return "targetRegion fehlt.";
  if (!Number.isInteger(body.companiesPerRun) || body.companiesPerRun < 1 || body.companiesPerRun > 50) {
    return "companiesPerRun muss eine Ganzzahl zwischen 1 und 50 sein.";
  }
  if (typeof body.driveFolderUrl !== "string") return "driveFolderUrl muss ein Text sein (kann leer sein).";
  if (!Array.isArray(body.times) || body.times.length === 0) return "times muss eine nicht-leere Liste sein.";
  for (const t of body.times) {
    if (typeof t !== "string" || !TIME_RE.test(t)) return `Ungültige Uhrzeit: ${t} (Format HH:MM erwartet).`;
  }
  for (const key of ["templateA", "templateB"]) {
    const tpl = body[key];
    if (typeof tpl !== "object" || tpl === null) return `${key} fehlt.`;
    if (typeof tpl.subject !== "string" || !tpl.subject.trim()) return `${key}.subject fehlt.`;
    if (typeof tpl.body !== "string" || !tpl.body.trim()) return `${key}.body fehlt.`;
  }
  return null;
}

app.get("/api/config", (req, res) => {
  res.json(readJson(CONFIG_PATH, {}));
});

app.put("/api/config", (req, res) => {
  const error = validateConfig(req.body);
  if (error) return res.status(400).json({ error });
  writeJson(CONFIG_PATH, req.body);
  res.json({ ok: true });
});

app.get("/api/pdfs", (req, res) => {
  const files = fs
    .readdirSync(PDF_DIR)
    .filter((f) => f.toLowerCase().endsWith(".pdf"))
    .map((f) => {
      const stat = fs.statSync(path.join(PDF_DIR, f));
      return { filename: f, sizeBytes: stat.size, uploadedAt: stat.mtime };
    });
  res.json(files);
});

const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, PDF_DIR),
    filename: (req, file, cb) => {
      const safeName = path
        .basename(file.originalname)
        .replace(/[^a-zA-Z0-9._-]/g, "_");
      cb(null, `${Date.now()}-${safeName}`);
    },
  }),
  fileFilter: (req, file, cb) => {
    if (file.mimetype !== "application/pdf") {
      return cb(new Error("Nur PDF-Dateien sind erlaubt."));
    }
    cb(null, true);
  },
  limits: { fileSize: 20 * 1024 * 1024 },
});

app.post("/api/pdfs", upload.single("pdf"), (req, res) => {
  if (!req.file) return res.status(400).json({ error: "Keine Datei empfangen." });
  res.json({ ok: true, filename: req.file.filename });
});

app.delete("/api/pdfs/:filename", (req, res) => {
  const safeName = path.basename(req.params.filename);
  const target = path.join(PDF_DIR, safeName);
  if (!target.startsWith(PDF_DIR)) return res.status(400).json({ error: "Ungültiger Dateiname." });
  if (!fs.existsSync(target)) return res.status(404).json({ error: "Datei nicht gefunden." });
  fs.unlinkSync(target);
  res.json({ ok: true });
});

app.get("/api/contacted", (req, res) => {
  res.json(readJson(CONTACTED_PATH, []));
});

app.use((err, req, res, next) => {
  res.status(400).json({ error: err.message || "Unbekannter Fehler." });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Email-Automation-Server läuft auf http://localhost:${PORT}`);
});
