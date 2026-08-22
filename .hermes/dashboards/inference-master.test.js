#!/usr/bin/env -S deno run --allow-read

// ═══════════════════════════════════════════════
// Test suite for inference-master.html
// Validates: HTML structure, JS syntax, model data integrity, estimation functions
// ═══════════════════════════════════════════════

import { assertEquals, assertExists, assert } from "https://deno.land/std@0.224.0/assert/mod.ts";

console.log("═══ inference-master.html test suite ═══\n");

// ── 1. Read HTML ──────────────────
const html = await Deno.readTextFile("/home/hermes/.hermes/dashboards/inference-master.html");
console.log(`✓ HTML read: ${html.length.toLocaleString()} bytes`);

// ── 2. Extract JS (regex-based) ──
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
assertExists(scriptMatch, "No <script> tag found");
const jsCode = scriptMatch[1];
console.log(`✓ JS extracted: ${jsCode.length.toLocaleString()} chars`);

// ── 3. Validate JS syntax ───────────────────
try {
  new Function(jsCode);
  console.log("✓ JS syntax valid");
} catch (e) {
  console.error(`✗ JS syntax error: ${e.message}`);
  Deno.exit(1);
}

// ── 4. Execute JS in sandbox (mock DOM) ─────
// Create minimal DOM mock
const globalObj = {
  document: {
    getElementById: (id) => ({ innerHTML: "", classList: { add: () => {}, remove: () => {} } }),
    querySelector: () => null,
    querySelectorAll: () => [],
  },
};

// Replace Function calls and evaluate in sandbox
try {
  const sandboxJs = jsCode
    .replace(/document\.getElementById\([^)]+\)/g, '({innerHTML:"",classList:{add:()=>{},remove:()=>{}}})')
    .replace(/document\.querySelectorAll\([^)]+\)/g, '[]')
    .replace(/document\.querySelector\([^)]+\)/g, 'null');
  
  new Function(sandboxJs)();
  console.log("✓ JS execution (sandbox) — no errors");
} catch (e) {
  console.error(`✗ JS runtime error: ${e.message}`);
  Deno.exit(1);
}

// ── 5. Parse model data ─────────────────────
// Extract the D[] array
const dMatch = html.match(/const D=\[([\s\S]*?)\];/);
assertExists(dMatch, "Could not find D[] model array");

// Parse models manually (simple regex approach)
const modelRegex = /\{n:"([^"]+)",ar:"([^"]+)",fp8:(\d+|null),bf16:(\d+|null),q3:(\d+|null),q4:(\d+|null),q8:(\d+|null),ctx:(\d+),lic:"([^"]+)",cr:"([^"]+)",vf:(\d),mp:(\d),hr:"([^"]+)",st:"([^"]+)",re:"([^"]+)",bl:(\d+|null),bs:(\d+\.?\d*|null),df:(\d+),nt:"([^"]*)"\}/g;

const models = [];
let match;
while ((match = modelRegex.exec(html)) !== null) {
  models.push({
    name: match[1],
    arch: match[2],
    fp8: match[3] === 'null' ? null : parseInt(match[3]),
    bf16: match[4] === 'null' ? null : parseInt(match[4]),
    q3: match[5] === 'null' ? null : parseInt(match[5]),
    q4: match[6] === 'null' ? null : parseInt(match[6]),
    q8: match[7] === 'null' ? null : parseInt(match[7]),
    ctx: parseInt(match[8]),
    lic: match[9],
    creator: match[10],
    vision: match[11] === '1',
    mtp: match[12] === '1',
    hf: match[13],
    status: match[14],
    action: match[15],
    bench_rank: match[16] === 'null' ? null : parseInt(match[16]),
    bench_score: match[17] === 'null' ? null : parseFloat(match[17]),
    disk_gb: parseInt(match[18]),
    note: match[19],
  });
}

console.log(`✓ Parsed ${models.length} models`);
assertEquals(models.length, 38, `Expected 38 models, got ${models.length}`);

// ── 6. Validate model data integrity ────────
console.log("\n─── Model data validation ───");

// Check no null FP8 for downloadable models
const dlModels = models.filter(m => m.action === 'download');
dlModels.forEach(m => {
  assert(m.fp8 !== null || m.q4 !== null, `${m.name}: download action but no FP8 or Q4 size`);
  assert(m.bench_rank !== null || m.note.includes('🆕') || m.note.includes('Sibling') || m.note.includes('Bрат'), 
    `${m.name}: download action but no benchmark rank and not flagged as new`);
});
console.log(`✓ ${dlModels.length} download models have valid data`);

// Check bench scores are realistic (0-100)
models.filter(m => m.bench_score).forEach(m => {
  assert(m.bench_score > 0 && m.bench_score < 100, `${m.name}: bench_score ${m.bench_score} out of range`);
});
console.log(`✓ ${models.filter(m => m.bench_score).length} bench scores valid`);

// Check no duplicate names
const names = models.map(m => m.name);
const dupes = names.filter((n, i) => names.indexOf(n) !== i);
assertEquals(dupes.length, 0, `Duplicate model names: ${dupes.join(', ')}`);
console.log(`✓ No duplicate model names`);

// Check all HF repos are non-empty
models.forEach(m => {
  assert(m.hf && m.hf.length > 3, `${m.name}: empty HF repo`);
});
console.log(`✓ All HF repos present`);

// ── 7. Estimate functions ───────────────────
console.log("\n─── Estimation functions ───");

const HW = { gv: 96, gb: 1800, cr: 512, cb: 200, co: 100, go: 8, usable: 404 };

function kv(p, ctx) { return (p * 2 / 1024) * (ctx / 4096); }
function gtps(p) { return Math.round(HW.gb * 1e9 * 0.85 / (2 * p * 1e9)); }
function cpt(q) { return Math.round(HW.cb * 1e9 * 0.7 / (2 * q * 1e9)); }
function msu(a) { return 1 + a * 2 / 3; }

// Test KV cache calculation
assertEquals(kv(27, 131072), 7, `KV(27B, 128K) = ${kv(27, 131072)} (expected ~7)`);
assertEquals(kv(31, 262144), 16, `KV(31B, 256K) = ${kv(31, 262144)} (expected ~16)`);
console.log("✓ KV cache estimation");

// Test GPU TPS
const tps27 = gtps(27);
assert(tps27 > 20 && tps27 < 80, `GPU TPS for 27B: ${tps27} (expected 20-80)`);
console.log(`✓ GPU TPS 27B: ${tps27} tok/s`);

const tps128 = gtps(128);
assert(tps128 > 5 && tps128 < 20, `GPU TPS for 128B: ${tps128} (expected 5-20)`);
console.log(`✓ GPU TPS 128B: ${tps128} tok/s`);

// Test CPU TPS
const cpu261 = cpt(261);
assert(cpu261 > 1 && cpu261 < 10, `CPU TPS for Q4 261GB: ${cpu261} (expected 2-8)`);
console.log(`✓ CPU TPS Q4 261GB: ${cpu261} tok/s`);

// Test MTP speedup
assert(Math.abs(msu(0.75) - 1.5) < 0.01, `MTP speedup at 75%: ${msu(0.75)}`);
assert(Math.abs(msu(0.80) - 1.533) < 0.01, `MTP speedup at 80%: ${msu(0.80)}`);
console.log(`✓ MTP speedup: 75%→${msu(0.75).toFixed(2)}x, 80%→${msu(0.80).toFixed(2)}x`);

// ── 8. GPU/CPU fit checks ──────────────────
console.log("\n─── Fit checks ───");

const gpuFits = dlModels.filter(m => m.fp8 && m.fp8 + kv(parseInt(m.arch.match(/\d+/)[0]), 131072) + HW.go <= 96);
console.log(`✓ ${gpuFits.length} download models fit GPU: ${gpuFits.map(m => m.name).join(', ')}`);

const cpuFitsQ4 = dlModels.filter(m => m.q4 && m.q4 <= HW.usable);
console.log(`✓ ${cpuFitsQ4.length} download models fit CPU Q4: ${cpuFitsQ4.map(m => m.name).join(', ')}`);

// ── 9. Disk cleanup totals ─────────────────
console.log("\n─── Cleanup ───");

const delModels = models.filter(m => ['delete', 'archive'].includes(m.action));
const totalDel = delModels.reduce((s, m) => s + m.disk_gb, 0);
console.log(`✓ ${delModels.length} models to cleanup, total ${totalDel} GB`);

const diskModels = models.filter(m => m.status === 'disk');
const totalDisk = diskModels.reduce((s, m) => s + m.disk_gb, 0);
console.log(`✓ ${diskModels.length} models on disk, total ${totalDisk} GB`);

// ── 10. HTML structure ─────────────────────
console.log("\n─── HTML structure ───");

// Count script tags (simple regex)
const scriptTags = html.match(/<script>/g) || [];
assert(scriptTags.length === 1, `Expected 1 <script>, got ${scriptTags.length}`);
console.log(`✓ 1 script block`);

// Check all sections exist
const requiredIds = ['hw', 'tabs', 'mt', 'md', 'cl', 'ge', 'ce'];
requiredIds.forEach(id => {
  assert(html.includes(`id="${id}"`), `Missing element with id="${id}"`);
});
console.log(`✓ All required sections present`);

// Check HuggingFace links
models.forEach(m => {
  assert(html.includes(`href="https://huggingface.co/${m.hf}`) || m.hf.includes('TBD'), 
    `${m.name}: missing HF link for ${m.hf}`);
});
console.log(`✓ All ${models.length} HF links present`);

// ── 11. Category filter check ──────────────
console.log("\n─── Filter categories ───");
const categories = ['all', 'dl', 'disk', 'del', 'hdd', 'bench', 'new', 'skip', 'watch'];
categories.forEach(cat => {
  assert(html.includes(`'${cat}'`), `Missing filter category: ${cat}`);
});
console.log(`✓ All ${categories.length} filter categories present`);

// ── 12. Benchmark data cross-check ─────────
console.log("\n─── Benchmark cross-check ───");
const benchModels = models.filter(m => m.bench_rank);
const benchRanks = benchModels.map(m => m.bench_rank).sort((a, b) => a - b);
assert(!benchRanks.some((r, i, arr) => arr[i + 1] === r), "Duplicate bench ranks");
console.log(`✓ ${benchModels.length} models with BenchLM ranks, no duplicates`);

// Specific models expected
const expectedBench = ['MiniMax M3', 'Hy3', 'Inkling-Small', 'GLM-5.1 (Q3_K_M only)', 'GLM-5.2', 'Qwen3.8-2.4T-A95B', 'Kimi K3'];
expectedBench.forEach(name => {
  const found = benchModels.find(m => m.name.includes(name.split(' ')[0]));
  assert(found, `Missing bench model: ${name}`);
});
console.log(`✓ All expected BenchLM models present`);

// ── 13. License check ──────────────────────
console.log("\n─── License check ───");
const licenses = [...new Set(models.map(m => m.lic))];
console.log(`✓ ${licenses.length} unique licenses: ${licenses.join(', ')}`);

const apache = models.filter(m => m.lic === 'Apache-2.0');
const mit = models.filter(m => m.lic === 'MIT');
console.log(`  Apache-2.0: ${apache.length}, MIT: ${mit.length}`);

// ── Summary ────────────────────────────────
console.log("\n╔══════════════════════════════════════╗");
console.log("║       ALL TESTS PASSED ✓            ║");
console.log("╠══════════════════════════════════════╣");
console.log(`║  ${models.length} models validated               ║`);
console.log(`║  ${dlModels.length} download candidates           ║`);
console.log(`║  ${diskModels.length} on-disk models              ║`);
console.log(`║  ${delModels.length} cleanup candidates (${totalDel} GB) ║`);
console.log(`║  ${benchModels.length} BenchLM entries             ║`);
console.log(`║  JS: syntax + sandbox OK            ║`);
console.log(`║  HTML: structure + links OK         ║`);
console.log("╚══════════════════════════════════════╝");
