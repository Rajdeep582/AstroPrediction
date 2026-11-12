// One-time setup: frontend packages + isolated backend virtualenv.
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const win = process.platform === "win32";
const run = (cmd, cwd = root) => { console.log(`> ${cmd}`); execSync(cmd, { cwd, stdio: "inherit" }); };

run("npm install", path.join(root, "frontend"));
const backend = path.join(root, "backend");
const py = path.join(backend, ".venv", win ? "Scripts/python.exe" : "bin/python");
if (!existsSync(py)) run(`${win ? "py -3" : "python3"} -m venv .venv`, backend);
run(`"${py}" -m pip install --upgrade pip`, backend);
run(`"${py}" -m pip install -r requirements.txt`, backend);
console.log("\nSetup complete. Start everything with: npm run dev");
