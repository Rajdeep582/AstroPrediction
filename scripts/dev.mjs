// Starts backend (8800) and frontend (4000). `node scripts/dev.mjs api|web` starts just one.
// Checks ports first, waits for the API to be healthy before starting the web app, Ctrl+C stops all.
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import net from "node:net";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const win = process.platform === "win32";
const prod = process.argv.includes("--prod");
const only = process.argv.slice(2).find((a) => a === "api" || a === "web");
const py = path.join(root, "backend", ".venv", win ? "Scripts/python.exe" : "bin/python");
const API = { name: "api", port: 8800, color: 35 };
const WEB = { name: "web", port: 4000, color: 33 };

const tag = (s) => `\x1b[${s.color}m[${s.name}]\x1b[0m `;
const portBusy = (port) => new Promise((res) => {
  const srv = net.createServer().once("error", () => res(true)).once("listening", () => srv.close(() => res(false)));
  srv.listen(port); // all interfaces (IPv4 + IPv6), catches Next.js on :::port
});

async function waitForApi(ms = 30000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    try {
      const r = await fetch(`http://127.0.0.1:${API.port}/api/health`);
      if (r.ok) { const h = await r.json(); if (h.database !== "connecting") return h; }
    } catch {}
    await new Promise((r) => setTimeout(r, 400));
  }
  return null;
}

const procs = [];
let stopping = false;
function stop(code = 0) {
  if (stopping) return; stopping = true;
  for (const p of procs) {
    if (p.exitCode !== null) continue;
    if (win) spawn("taskkill", ["/pid", String(p.pid), "/t", "/f"], { stdio: "ignore" }); else p.kill("SIGTERM");
  }
  setTimeout(() => process.exit(code), 800);
}
process.on("SIGINT", () => stop()); process.on("SIGTERM", () => stop());

function start(svc, cmd, args, cwd) {
  const shell = win && cmd === "npm";
  const p = spawn(shell ? [cmd, ...args].join(" ") : cmd, shell ? [] : args, { cwd, shell, detached: win, windowsHide: true, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, PORT: String(svc.port), API_PORT: String(API.port), PYTHONUNBUFFERED: "1", FORCE_COLOR: "1" } });
  const out = (d) => process.stdout.write(d.toString().replace(/^(?=.)/gm, tag(svc)));
  p.stdout.on("data", out); p.stderr.on("data", out);
  p.on("exit", (code) => { if (!stopping) { console.log(`${tag(svc)}exited with code ${code}`); stop(code ?? 1); } });
  procs.push(p);
}

const wantApi = only !== "web", wantWeb = only !== "api";
for (const s of [wantApi && API, wantWeb && WEB].filter(Boolean)) {
  if (await portBusy(s.port)) {
    console.error(`${tag(s)}port ${s.port} is already in use — another copy is probably running. Stop it first.`);
    process.exit(1);
  }
}

if (wantApi) {
  if (!existsSync(py)) { console.error("Backend virtualenv missing. Run: npm run setup"); process.exit(1); }
  start(API, py, prod ? ["run.py", "--prod"] : ["run.py"], path.join(root, "backend"));
  const health = await waitForApi();
  if (!health) console.error(`${tag(API)}did not become healthy within 30s — see the log above.`);
  else console.log(`${tag(API)}ready → http://localhost:${API.port}  (database: ${health.database}${health.database_error ? ` — ${health.database_error}` : ""})`);
}
if (wantWeb) {
  start(WEB, "npm", ["run", prod ? "start" : "dev"], path.join(root, "frontend"));
  console.log(`${tag(WEB)}starting → http://localhost:${WEB.port}`);
}
