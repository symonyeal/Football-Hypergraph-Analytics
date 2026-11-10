// Draws site/data.js (written by `python -m fha.site`). Two calculations are repeated here and certified against
// Python: coverage of a chosen player set (checked against the published best-set coverage) and the defence
// model's probability (checked on synthetic frames). Colours are the theme tokens in style.css.
"use strict";

const D = window.DATA, $ = (id) => document.getElementById(id);
const css = getComputedStyle(document.documentElement), tok = (k) => css.getPropertyValue("--" + k).trim();
const T = Object.fromEntries(["bg", "text", "text-2", "muted", "border", "axis", "context", "accent", "accent-2", "c3", "font"].map((k) => [k, tok(k)]));
const AX = { gridcolor: T.border, zerolinecolor: T.axis, linecolor: T.axis, automargin: true, tickfont: { color: T["text-2"] }, title: { font: { color: T["text-2"] } } };
const pct = (x, d = 0) => (100 * x).toFixed(d) + "%";
const fx = (x, d = 2) => (x == null ? "—" : Number(x).toFixed(d));
const ci = (v) => `${fx(v[1][0])} to ${fx(v[1][1])}`;

function plot(id, data, layout = {}) {
  const narrow = innerWidth < 700;
  Plotly.react($(id), data, {
    height: layout.height || (narrow ? 340 : 420), paper_bgcolor: T.bg, plot_bgcolor: T.bg, showlegend: false,
    font: { family: T.font, color: T.text, size: 13 }, margin: { t: 16, r: narrow ? 24 : 40, b: 52, l: 60 },
    hoverlabel: { bgcolor: T.bg, bordercolor: T.border, font: { color: T.text } },
    ...layout, xaxis: { ...AX, ...layout.xaxis }, yaxis: { ...AX, ...layout.yaxis },
  }, { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] });
}

function seg(id, values, labels, get, set) {
  const el = $(id);
  el.replaceChildren(...values.map((v, i) => {
    const b = document.createElement("button");
    b.textContent = labels[i];
    b.dataset.v = v;
    b.onclick = () => { set(v); sync(); };
    return b;
  }));
  const sync = () => el.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === get()));
  sync();
}

// ------------------------------------------------------------------ attack
const A = D.attack, NM = A ? A.names : {};
const name = (p) => NM[String(p)] || String(p);
const short = name;   // full StatsBomb names: Iberian surnames make any first-plus-last shortening wrong

/** Share of xG in groups G = [[players], possessions, xG] meeting the set S. */
function covered(S, G) {
  let a = 0, w = 0;
  for (const [P, , x] of G) { w += x; if (P.some((p) => S.has(p))) a += x; }
  return w ? a / w : 0;
}

const S = { metric: "tau", league: "All", team: null, sel: new Set(), key: "bottleneck", dm: "hole" };
const METRICS = { tau: ["Fewest players touching every chance", "τ"], nu: ["Chances sharing no player", "ν"],
  cov2: ["Share of xG two players touch", "cov(2)"], tau_star: ["Fractional fewest players", "τ*"] };
const val = (t, W, k) => (k === "cov2" ? t[W].cov["2"][0] : t[W][k]);

function drawStable() {
  const teams = Object.entries(A.teams).filter(([, t]) => S.league === "All" || t.league === S.league);
  const jit = (s) => (S.metric === "tau" || S.metric === "nu" ? ((s.charCodeAt(0) * 7 + s.length * 13) % 9 - 4) * 0.05 : 0);
  const x = teams.map(([n, t]) => val(t, "train", S.metric) + jit(n)), y = teams.map(([n, t]) => val(t, "test", S.metric) + jit(n + "x"));
  const lo = Math.min(...x, ...y), hi = Math.max(...x, ...y), lab = METRICS[S.metric];
  plot("stable-chart", [
    { x: [lo, hi], y: [lo, hi], mode: "lines", line: { color: T.context, width: 1, dash: "dot" }, hoverinfo: "skip" },
    { x, y, mode: "markers", marker: { color: T.accent, size: 9, line: { color: T.bg, width: 2 } },
      text: teams.map(([n, t]) => `${n} (${t.league})`),
      customdata: teams.map(([, t]) => [val(t, "train", S.metric), val(t, "test", S.metric)]),
      hovertemplate: "<b>%{customdata[0]:.2f} → %{customdata[1]:.2f}</b><br>%{text}<extra></extra>" },
  ], { xaxis: { title: { text: `${lab[0]} (${lab[1]}), first half` } }, yaxis: { title: { text: `${lab[1]}, second half` } } });
  const r = A.H1[S.metric === "cov2" ? "cov2" : S.metric];
  $("stable-take").textContent = `${lab[0]}: correlation between halves ${fx(r[0])} (95% interval ${ci(r)}), all 80 teams. ` +
    (r[1][0] > 0 ? "It is a property of the team, not noise." : "Not distinguishable from noise.");
}

function teamPlayers(t) {
  const inv = new Map();
  for (const [P, , x] of t.train.groups) for (const p of P) inv.set(p, (inv.get(p) || 0) + x);
  return [...inv.entries()].sort((a, b) => b[1] - a[1]).slice(0, 22).map(([p]) => p);
}

function drawMark() {
  const t = A.teams[S.team];
  const chips = teamPlayers(t).map((p) => {
    const b = document.createElement("button");
    b.className = "chip" + (S.sel.has(p) ? " on" : "");
    b.textContent = short(p);
    b.title = name(p);
    b.setAttribute("aria-pressed", S.sel.has(p));
    b.onclick = () => { S.sel.has(p) ? S.sel.delete(p) : S.sel.add(p); drawMark(); };
    return b;
  });
  $("mark-chips").replaceChildren(...chips);
  const a = covered(S.sel, t.train.groups), b = covered(S.sel, t.test.groups);
  const r = $("mark-readout");
  r.replaceChildren();
  for (const [v, l, alt] of [[pct(a), "of first-half danger", false], [pct(b), "of second-half danger", true], [String(S.sel.size), "players marked", false]]) {
    const d = document.createElement("div");
    if (alt) d.className = "alt";
    const bb = document.createElement("b"); bb.textContent = v;
    const s = document.createElement("span"); s.textContent = l;
    d.append(bb, s); r.append(d);
  }
  $("mark-team-note").textContent = `${S.team}, first half: ${t.train.m} chances, ${fx(t.train.xg, 1)} xG. ` +
    `Fewest players touching every chance: ${t.train.tau} (second half ${t.test.tau}). Chances sharing no player: ` +
    `${t.train.nu} (${t.test.nu}). Solo chances: ${pct(t.train.solo)} of xG.`;
  const B = [1, 2, 3, 4, 5];
  const best = B.map((k) => t.train.cov[k][0]);
  const bestTest = B.map((k) => covered(new Set(t.train.cov[k][1]), t.test.groups));
  const useTest = B.map((k) => covered(new Set(t.train.usage.slice(0, k)), t.test.groups));
  const lines = [
    [best, "Best set, first half", T.context, "dot"], [bestTest, "Best first-half set, second half", T.accent, "solid"],
    [useTest, "Most touches, second half", T["accent-2"], "solid"]];
  const tr = lines.map(([y, n, c, dash]) => ({ x: B, y, mode: "lines+markers", line: { color: c, width: 2, dash }, marker: { size: 8, color: c },
    name: n, hovertemplate: `<b>%{y:.0%}</b> ${n}<br>%{x} players<extra></extra>` }));
  if (S.sel.size) tr.push({ x: [S.sel.size], y: [b], mode: "markers", name: "Your selection, second half", marker: { size: 14, color: T.text, symbol: "diamond" },
    hovertemplate: `<b>${pct(b)}</b> your selection, second half<extra></extra>` });
  plot("mark-chart", tr, { showlegend: true, legend: { orientation: "h", x: 0, y: 1.18, font: { color: T["text-2"], size: 12 } }, margin: { t: 64, r: 24, b: 52, l: 60 },
    xaxis: { title: { text: "players marked" }, dtick: 1, range: [0.7, 5.3] }, yaxis: { title: { text: "share of danger touched" }, tickformat: ".0%", range: [0, 1] } });
  const G = [...t.train.groups].sort((x, y) => y[2] - x[2]).slice(0, 10);
  const tb = $("mark-groups");
  tb.replaceChildren();
  const h = tb.insertRow();
  for (const c of ["Last three players before the shot", "Chances", "xG"]) { const th = document.createElement("th"); th.textContent = c; h.append(th); }
  for (const [P, n, x] of G) {
    const row = tb.insertRow();
    row.insertCell().textContent = P.map(short).join(", ");
    const c1 = row.insertCell(); c1.textContent = n; c1.className = "num";
    const c2 = row.insertCell(); c2.textContent = fx(x); c2.className = "num";
  }
}

function setSel(ids) { S.sel = new Set(ids); drawMark(); }

function drawMissing() {
  const h = A.H3[S.key], rows = h.teams;
  plot("missing-chart", [{
    x: rows.map((r) => A.teams[r[0]].train.nu), y: rows.map((r) => r[4]), mode: "markers",
    marker: { color: T.accent, size: 10, line: { color: T.bg, width: 2 } },
    text: rows.map((r) => `${r[0]}: ${r[1]} missed ${r[2]}, started ${r[3]}`),
    hovertemplate: "<b>drop %{y:.0%}</b><br>%{text}<br>separate routes %{x}<extra></extra>",
  }], { xaxis: { title: { text: "chances sharing no player (ν), first half" } }, yaxis: { title: { text: "drop in xG when the player is missing" }, tickformat: ".0%", zeroline: true } });
  const r = h.rho_nu;
  $("missing-take").textContent = r ? `Correlation ${fx(r[0])} (95% interval ${ci(r)}), ${rows.length} teams: the expected direction, but not resolved.` : "";
}

// ------------------------------------------------------------------ defence
const DF = D.defence;

function features(P, ball) {
  const n = P.length;
  // Euclidean minimum spanning tree (Prim); gap = its longest edge
  const inT = new Array(n).fill(false), best = new Array(n).fill(Infinity), par = new Array(n).fill(-1);
  best[0] = 0; const E = [];
  for (let k = 0; k < n; k++) {
    let u = -1;
    for (let i = 0; i < n; i++) if (!inT[i] && (u < 0 || best[i] < best[u])) u = i;
    inT[u] = true;
    if (par[u] >= 0) E.push([par[u], u, best[u]]);
    for (let v = 0; v < n; v++) if (!inT[v]) { const d = Math.hypot(P[u][0] - P[v][0], P[u][1] - P[v][1]); if (d < best[v]) { best[v] = d; par[v] = u; } }
  }
  const gap = Math.max(...E.map((e) => e[2]));
  const dl = Delaunator.from(P), H = Array.from(dl.hull).map((i) => P[i]);
  let area = 0;
  for (let i = 0; i < H.length; i++) { const a = H[i], b = H[(i + 1) % H.length]; area += a[0] * b[1] - b[0] * a[1]; }
  area = Math.abs(area) / 2;
  const sgn = Math.sign(area === 0 ? 1 : H.reduce((s, a, i) => { const b = H[(i + 1) % H.length]; return s + a[0] * b[1] - b[0] * a[1]; }, 0));
  const inside = (q) => H.every((a, i) => { const b = H[(i + 1) % H.length]; return sgn * ((b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])) >= -1e-9; });
  let hole = 0, ho = null;
  for (let t = 0; t < dl.triangles.length; t += 3) {
    const [a, b, c] = [P[dl.triangles[t]], P[dl.triangles[t + 1]], P[dl.triangles[t + 2]]];
    const d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]));
    const aa = a[0] ** 2 + a[1] ** 2, bb = b[0] ** 2 + b[1] ** 2, cc = c[0] ** 2 + c[1] ** 2;
    const u = [(aa * (b[1] - c[1]) + bb * (c[1] - a[1]) + cc * (a[1] - b[1])) / d, (aa * (c[0] - b[0]) + bb * (a[0] - c[0]) + cc * (b[0] - a[0])) / d];
    const r = Math.hypot(u[0] - a[0], u[1] - a[1]);
    if (r > hole && inside(u)) { hole = r; ho = u; }
  }
  const xs = P.map((p) => p[0]), ys = P.map((p) => p[1]);
  return { f: { x: ball[0], yy: ball[1], dist: Math.hypot(105 - ball[0], 34 - ball[1]), width: Math.max(...ys) - Math.min(...ys),
    depth: Math.max(...xs) - Math.min(...xs), area, gap, hole }, E, H, ho };
}

function prob(m, f) {
  let z = m.intercept;
  m.cols.forEach((c, i) => { z += m.coef[i] * (f[c] - m.mean[i]) / m.scale[i]; });
  return 1 / (1 + Math.exp(-z));
}

const BLOCKS = {
  base: [[90, 14], [90, 27], [90, 41], [90, 54], [80, 12], [80, 26], [80, 42], [80, 56], [68, 27], [68, 41]],
  compact: [[93, 21], [93, 30], [93, 38], [93, 47], [86, 19], [86, 29], [86, 39], [86, 49], [77, 29], [77, 39]],
  stretch: [[97, 6], [95, 24], [95, 44], [97, 62], [74, 8], [74, 26], [74, 42], [74, 60], [58, 24], [58, 44]],
  hole: [[92, 12], [92, 22], [92, 46], [92, 56], [80, 10], [80, 22], [80, 46], [80, 58], [68, 27], [68, 41]],
};
const DS = { P: BLOCKS.base.map((p) => p.slice()), ball: [66, 34] };
const NS = "http://www.w3.org/2000/svg";
const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent && parent.append(e); return e; };

function pitchLines(svg) {
  const g = el("g", {}, svg);
  el("rect", { x: 0, y: 0, width: 105, height: 68, class: "line" }, g);
  el("line", { x1: 52.5, y1: 0, x2: 52.5, y2: 68, class: "line" }, g);
  el("circle", { cx: 52.5, cy: 34, r: 9.15, class: "line" }, g);
  el("rect", { x: 89.25, y: 15.3, width: 15.75, height: 37.4, class: "line" }, g);
  el("rect", { x: 99.75, y: 24.85, width: 5.25, height: 18.3, class: "line" }, g);
  el("rect", { x: 0, y: 15.3, width: 15.75, height: 37.4, class: "line" }, g);
}

function drawDefence() {
  const svg = $("pitch");
  svg.replaceChildren();
  pitchLines(svg);
  const { f, E, H, ho } = features(DS.P, DS.ball);
  el("polygon", { points: H.map((p) => p.join(",")).join(" "), class: "hull" }, svg);
  if (ho) el("circle", { cx: ho[0], cy: ho[1], r: f.hole, class: "hole" }, svg);
  for (const [i, j, d] of E) el("line", { x1: DS.P[i][0], y1: DS.P[i][1], x2: DS.P[j][0], y2: DS.P[j][1], class: d === f.gap ? "mst gap" : "mst" }, svg);
  DS.P.forEach((p, i) => drag(el("circle", { cx: p[0], cy: p[1], r: 1.4, class: "def", tabindex: 0, "aria-label": `defender ${i + 1}` }, svg), p));
  drag(el("circle", { cx: DS.ball[0], cy: DS.ball[1], r: 1.1, class: "ball", tabindex: 0, "aria-label": "ball" }, svg), DS.ball);
  const pg = prob(DF.model.gaps, f), ps = prob(DF.model.shape, f), pb = prob(DF.model.base, f);
  const inBox = DS.ball[0] >= 89.25 && DS.ball[1] >= 15.3 && DS.ball[1] <= 52.7, own = DS.ball[0] < 52.5;
  const r = $("def-readout");
  r.replaceChildren();
  for (const [v, l, alt] of [[pct(pg, 1), "chance of a box entry within 10 s (full model)", false],
    [pct(pb, 1), "from ball position alone", true], [fx(f.gap, 1) + " m", "widest gap between neighbours", false],
    [fx(f.hole, 1) + " m", "radius of the largest empty circle", false], [fx(f.width, 0) + " × " + fx(f.depth, 0) + " m", "block width × depth", false]]) {
    const d = document.createElement("div"); if (alt) d.className = "alt";
    const b = document.createElement("b"); b.textContent = v; const s = document.createElement("span"); s.textContent = l;
    d.append(b, s); r.append(d);
  }
  const w = document.createElement("p");
  w.className = "note" + (inBox || own ? " warn" : "");
  w.textContent = inBox || own ? "Outside the model's data: passes were taken from the opponent half, outside the box."
    : `Shape alone gives ${pct(ps, 1)}; the gap and hole move it to ${pct(pg, 1)}.`;
  r.append(w);
}

function drag(c, p) {
  const svg = $("pitch");
  const move = (e) => {
    const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    const q = pt.matrixTransform(svg.getScreenCTM().inverse());
    p[0] = Math.max(0, Math.min(105, q.x)); p[1] = Math.max(0, Math.min(68, q.y));
    requestAnimationFrame(drawDefence);
  };
  c.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    const up = () => { removeEventListener("pointermove", move); removeEventListener("pointerup", up); };
    addEventListener("pointermove", move); addEventListener("pointerup", up);
  });
  c.addEventListener("keydown", (e) => {
    const k = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
    if (!k) return;
    e.preventDefault(); p[0] += k[0]; p[1] += k[1]; drawDefence();
  });
}

function defCheck() {
  let dp = 0, df = 0;
  for (const c of DF.checks) {
    const { f } = features(c.P, c.ball);
    dp = Math.max(dp, Math.abs(prob(DF.model.gaps, f) - c.p));
    for (const k of ["gap", "hole", "area", "width", "depth"]) df = Math.max(df, Math.abs(f[k] - c.f[k]) / Math.max(1, Math.abs(c.f[k])));
  }
  const ok = dp < 1e-6 && df < 1e-6;
  $("def-check").className = "note " + (ok ? "ok" : "warn");
  $("def-check").textContent = `Browser model ${ok ? "matches" : "DOES NOT match"} the Python model on ${DF.checks.length} synthetic test frames ` +
    `(largest difference: probability ${dp.toExponential(1)}, geometry ${df.toExponential(1)} relative).`;
}

function drawDefQ() {
  const q = DF[`${S.dm}_quartiles_m`], e = DF[`${S.dm}_entry_rate_by_quartile`];
  const labels = [0, 1, 2, 3].map((i) => `${fx(q[i], 1)}–${fx(q[i + 1], 1)} m`);
  plot("def-q-chart", [{ x: labels, y: e, type: "bar", marker: { color: T.accent }, text: e.map((v) => pct(v)), textposition: "outside",
    hovertemplate: "<b>%{y:.1%}</b> box-entry rate<br>%{x}<extra></extra>", cliponaxis: false }],
    { height: 300, xaxis: { title: { text: `${S.dm}, quarters of all passes (smallest to largest)` } }, yaxis: { title: { text: "box-entry rate" }, tickformat: ".0%", rangemode: "tozero" } });
}

function drawDefGain() {
  const rows = [["Defensive shape over ball position", DF.shape_vs_base], ["Gap and hole over shape", DF.H5a_gaps_vs_shape], ["Topology (h1) over gap and hole", DF.H5b_topology_vs_gaps]];
  const y = rows.map((r) => r[0]), x = rows.map((r) => -1000 * r[1][0]);
  plot("def-gain-chart", [{ y, x, type: "bar", orientation: "h", marker: { color: [T.context, T.accent, T.context] },
    error_x: { type: "data", symmetric: false, array: rows.map((r) => -1000 * r[1][1][0] - -1000 * r[1][0]), arrayminus: rows.map((r) => -1000 * r[1][0] - -1000 * r[1][1][1]), color: T.muted },
    hovertemplate: "<b>%{x:.2f}</b> thousandths of log loss<br>%{y}<extra></extra>" }],
    { height: 240, margin: { t: 8, r: 24, b: 52, l: 250 }, xaxis: { title: { text: "improvement in test log loss (×1000), 95% interval" }, zeroline: true }, yaxis: { autorange: "reversed" } });
}

// ------------------------------------------------------------------ sequence and ratings
function drawSequence() {
  const q = D.sequence;
  if (!q) { $("sequence").hidden = true; return; }
  const rows = [["Action features (VAEP) over context", "d20"], ["Players and pass pairs over context", "d10"], ["Pass motif over players", "d31"],
    ["Players, pairs and motif over VAEP", "d42"], ["Player set over everything else", "d54"]];
  plot("seq-chart", [{ y: rows.map((r) => r[0]), x: rows.map((r) => -1000 * q[r[1]][0]), type: "bar", orientation: "h",
    marker: { color: rows.map((r) => (r[1] === "d54" ? T.accent : T.context)) },
    error_x: { type: "data", symmetric: false, array: rows.map((r) => 1000 * (q[r[1]][0] - q[r[1]][1][0])), arrayminus: rows.map((r) => 1000 * (q[r[1]][1][1] - q[r[1]][0])), color: T.muted },
    hovertemplate: "<b>%{x:.2f}</b><br>%{y}<extra></extra>" }],
    { height: 300, margin: { t: 8, r: 24, b: 52, l: 260 }, xaxis: { title: { text: "improvement in test log loss (×1000), 95% interval" }, zeroline: true }, yaxis: { autorange: "reversed" } });
  const holds = q.H4.holds;
  $("seq-h").textContent = holds ? "Who is on the ball predicts a shot beyond what they do and where" : "Who is on the ball adds no demonstrated information beyond what they do and where";
  $("seq-note").textContent = `Possessions alive after three on-ball actions: ${q.n.train.toLocaleString()} first-half, ${q.n.test.toLocaleString()} second-half; ` +
    `${pct(q.rate.test, 1)} go on to an open-play shot. Logistic models with the same tuning; positive bars mean the added block improves predictions on the second half.`;
  $("seq-take").textContent = `Registered threshold for the player set: ${fx(1000 * q.H4.threshold)} thousandths. Result: ${fx(-1000 * q.d54[0])} (${fx(-1000 * q.d54[1][1])} to ${fx(-1000 * q.d54[1][0])}).`;
}

function drawRatings() {
  const L = D.lineup;
  if (!L || !L.top) { $("ratings").hidden = true; return; }
  const rows = [...L.top.map((r) => [r[0], r[1]]), ...L.bottom.map((r) => [r[0], r[1]]).reverse()];
  plot("rat-chart", [{ y: rows.map((r) => r[0]), x: rows.map((r) => r[1]), type: "bar", orientation: "h",
    marker: { color: rows.map((r) => (r[1] >= 0 ? T.accent : T["accent-2"])) }, hovertemplate: "<b>%{x:+.3f}</b> xG/90<br>%{y}<extra></extra>" }],
    { height: 760, margin: { t: 8, r: 24, b: 52, l: 220 }, xaxis: { title: { text: "team xG difference per 90 with the player on, others held fixed" }, zeroline: true }, yaxis: { autorange: "reversed", tickfont: { size: 11 } } });
  const h = L.H6;
  $("rat-h").textContent = `Player ratings repeat between halves (correlation ${fx(h[0])}), but the top of the list is mostly three clubs`;
  $("rat-note").textContent = `${L.eligible_both} players with at least 900 minutes on and 270 team minutes off in both halves. Interval ${ci(h)}. ` +
    "With few substitutions and heavy shrinkage, a strong team's xG difference is shared among its regulars, so these ratings carry team strength (docs/POSTHOC.md, P2).";
}

// ------------------------------------------------------------------ wiring
function facts() {
  const F = [];
  if (A) F.push([fx(A.H1.tau[0]), "correlation of a team's concentration between half-seasons"], ["+" + fx(100 * A.H2.T_minus_U[0], 1) + " pts", "later danger covered by transversal sets over most-touched players"]);
  if (DF) F.push([pct(DF.rate.test), "of opponent-half passes reach the box within 10 s"]);
  if (D.lineup && D.lineup.H6) F.push([fx(D.lineup.H6[0]), "split-half correlation of player ratings"]);
  $("facts").replaceChildren(...F.map(([v, l]) => { const d = document.createElement("div"); const b = document.createElement("b"); b.textContent = v; const s = document.createElement("span"); s.textContent = l; d.append(b, s); return d; }));
}

facts();
if (A) {
  seg("c-metric", Object.keys(METRICS), Object.values(METRICS).map((m) => m[1] + ": " + m[0]), () => S.metric, (v) => { S.metric = v; drawStable(); });
  const lg = ["All", ...new Set(Object.values(A.teams).map((t) => t.league))].sort((a, b) => (a === "All" ? -1 : b === "All" ? 1 : a.localeCompare(b)));
  seg("c-league", lg, lg, () => S.league, (v) => { S.league = v; drawStable(); });
  const sel = $("c-team");
  for (const n of Object.keys(A.teams).sort()) { const o = document.createElement("option"); o.value = n; o.textContent = n; sel.append(o); }
  S.team = A.teams["Barcelona"] ? "Barcelona" : sel.value;
  sel.value = S.team;
  const t0 = () => A.teams[S.team];
  sel.onchange = () => { S.team = sel.value; setSel(t0().train.cov["2"][1]); };
  $("b-T").onclick = () => setSel(t0().train.T);
  $("b-C").onclick = () => setSel(t0().train.cov["2"][1]);
  $("b-U").onclick = () => setSel(t0().train.usage.slice(0, 2));
  $("b-clear").onclick = () => setSel([]);
  S.sel = new Set(t0().train.cov["2"][1]);
  seg("c-key", ["bottleneck", "usage"], ["Key player: top fractional weight", "Key player: most touches"], () => S.key, (v) => { S.key = v; drawMissing(); });
  drawStable(); drawMark(); drawMissing();
} else for (const id of ["stable", "mark", "missing"]) $(id).hidden = true;
if (DF) {
  $("b-compact").onclick = () => { DS.P = BLOCKS.compact.map((p) => p.slice()); drawDefence(); };
  $("b-stretch").onclick = () => { DS.P = BLOCKS.stretch.map((p) => p.slice()); drawDefence(); };
  $("b-hole").onclick = () => { DS.P = BLOCKS.hole.map((p) => p.slice()); drawDefence(); };
  seg("c-dmeasure", ["hole", "gap", "h1"], ["Largest empty circle", "Widest gap", "Topology h1"], () => S.dm, (v) => { S.dm = v; drawDefQ(); });
  drawDefence(); defCheck(); drawDefQ(); drawDefGain();
} else $("defence").hidden = true;
drawSequence(); drawRatings();
