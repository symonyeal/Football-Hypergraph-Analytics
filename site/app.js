// Draws site/data.js (written by `python -m fha.site`). The page filters, sorts and draws. Two calculations are
// repeated here and certified against Python when the page loads: coverage of a player set and the defence model.
"use strict";

const D = window.DATA, $ = (id) => document.getElementById(id);
const css = getComputedStyle(document.documentElement), tok = (k) => css.getPropertyValue("--" + k).trim();
const T = Object.fromEntries(["bg", "text", "text-2", "muted", "border", "axis", "context", "accent", "accent-2", "c3", "font"].map((k) => [k, tok(k)]));
const SLOT = ["c1", "accent-2", "c3", "c4", "c1", "accent-2"].map(tok);
const AX = { gridcolor: T.border, zerolinecolor: T.axis, linecolor: T.axis, automargin: true, tickfont: { color: T["text-2"] }, title: { font: { color: T["text-2"] } } };
const pct = (x, d = 0) => (x == null ? "—" : (100 * x).toFixed(d) + "%");
const fx = (x, d = 2) => (x == null ? "—" : Number(x).toFixed(d));
const ci = (v) => `${fx(v[1][0])} to ${fx(v[1][1])}`;
const make = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

function plot(id, data, layout = {}) {
  const n = data.reduce((a, t) => a + ((t.x && t.x.length) || 0), 0);
  if (!n) { Plotly.purge($(id)); $(id).replaceChildren(make("p", "empty", layout.empty || "Pick something above to fill this chart.")); return; }
  if ($(id).querySelector(".empty")) $(id).replaceChildren();
  const narrow = innerWidth < 700;
  Plotly.react($(id), data, {
    height: layout.height || (narrow ? 320 : 380), paper_bgcolor: T.bg, plot_bgcolor: T.bg, showlegend: false,
    font: { family: T.font, color: T.text, size: 13 }, margin: { t: 16, r: narrow ? 16 : 32, b: 52, l: 60 },
    hoverlabel: { bgcolor: T.bg, bordercolor: T.border, font: { color: T.text } },
    ...layout, xaxis: { ...AX, ...layout.xaxis }, yaxis: { ...AX, ...layout.yaxis },
  }, { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] });
}

function seg(id, values, labels, get, set) {
  const el = $(id);
  el.replaceChildren(...values.map((v, i) => {
    const b = make("button", null, labels[i]);
    b.dataset.v = v;
    b.onclick = () => { set(v); sync(); };
    return b;
  }));
  const sync = () => el.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === get()));
  sync();
}

// ------------------------------------------------------------------ data model
const NM = D.names || {};
const name = (p) => NM[String(p)] || String(p);
const TS = D.seasons.teams;                                   // team-seasons
const COMP = Object.fromEntries(D.seasons.competitions.map((c) => [c.key, c]));
const year = (s) => parseInt(String(s).slice(0, 4), 10);
TS.forEach((t, i) => {
  const c = COMP[t.key];
  t.i = i; t.comp = c.competition; t.season = c.season; t.gender = c.gender; t.intl = c.international; t.yr = year(c.season);
  t.source = c.source || "StatsBomb";
  t.label = `${t.team}, ${c.competition} ${c.season}${t.source === "Wyscout" ? " (Wyscout)" : ""}`;
  t.top2 = t.cov["2"][0];
  // involvement of each player: share of the team's open-play xG from chances they were among the last three in
  const inv = new Map();
  for (const [P, n, x] of t.groups) for (const p of P) { const v = inv.get(p) || [0, 0]; v[0] += x; v[1] += n; inv.set(p, v); }
  t.inv = inv;
});

/** Share of xG in groups G = [[players], possessions, xG] meeting the set S. */
function covered(S, G) {
  let a = 0, w = 0;
  for (const [P, , x] of G) { w += x; if (P.some((p) => S.has(p))) a += x; }
  return w ? a / w : 0;
}

// certificate: the published best-set coverage is reproduced from the groups for every team-season
// (data.js holds 5 significant digits, so agreement is to about 1e-4)
const covErr = Math.max(0, ...TS.flatMap((t) => Object.values(t.cov).map(([s, P]) => Math.abs(covered(new Set(P), t.groups) - s))));
const covOK = covErr < 1e-4;

const S = {
  gender: "all", kind: "all", source: "all", comps: new Set(), q: "", teams: [], focus: null,
  players: [], pfocus: null, pq: "", measure: "top2", dm: "hole", metric: "tau",
};
const MEASURE = {
  top2: { label: "Share of danger involving the top two players", fmt: (v) => pct(v), get: (t) => t.top2, high: "more concentrated" },
  tau: { label: "Players needed so every chance involves one of them", fmt: (v) => String(v), get: (t) => t.tau, high: "more spread" },
  nu: { label: "Chances with no player in common (separate routes)", fmt: (v) => String(v), get: (t) => t.nu, high: "more separate routes" },
};

function pass(t) {
  if (S.gender !== "all" && t.gender !== S.gender) return false;
  if (S.source !== "all" && t.source !== S.source) return false;
  if (S.kind === "league" && t.intl) return false;
  if (S.kind === "tournament" && !t.intl) return false;
  if (S.comps.size && !S.comps.has(t.comp)) return false;
  return true;
}
const pool = () => TS.filter(pass);
function share(t, k, P) { const v = P.map(MEASURE[k].get), x = MEASURE[k].get(t); return v.filter((y) => y < x).length / Math.max(1, v.length - 1); }

// ------------------------------------------------------------------ filters
function drawFilters() {
  seg("f-gender", ["all", "male", "female"], ["Men and women", "Men", "Women"], () => S.gender, (v) => { S.gender = v; S.comps.clear(); redraw(); });
  seg("f-source", ["all", "StatsBomb", "Wyscout"], ["Both sources", "StatsBomb", "Wyscout"], () => S.source, (v) => { S.source = v; redraw(); });
  seg("f-kind", ["all", "league", "tournament"], ["Leagues and tournaments", "Leagues", "Tournaments"], () => S.kind, (v) => { S.kind = v; S.comps.clear(); redraw(); });
  const names = [...new Set(TS.filter((t) => (S.gender === "all" || t.gender === S.gender) && (S.kind === "all" || (S.kind === "league") !== t.intl)).map((t) => t.comp))].sort();
  $("f-comps").replaceChildren(...names.map((n) => {
    const b = make("button", "chip" + (S.comps.has(n) ? " on" : ""), `${n} (${TS.filter((t) => t.comp === n).length})`);
    b.setAttribute("aria-pressed", S.comps.has(n));
    b.onclick = () => { S.comps.has(n) ? S.comps.delete(n) : S.comps.add(n); redraw(); };
    return b;
  }));
  const P = pool();
  $("f-count").textContent = `${P.length} team-seasons match the filters (teams with at least 5 matches and 15 chances).`;
}

// ------------------------------------------------------------------ teams
function teamList() {
  const q = S.q.toLowerCase();
  const rows = pool().filter((t) => !q || t.label.toLowerCase().includes(q))
    .sort((a, b) => a.comp.localeCompare(b.comp) || b.yr - a.yr || a.team.localeCompare(b.team));
  const ul = $("team-list");
  ul.replaceChildren();
  if (!rows.length) { ul.append(make("li", "empty", "No team-season matches the search and filters.")); return; }
  let head = null;
  for (const t of rows.slice(0, 400)) {
    const h = `${t.comp} ${t.season}${t.source === "Wyscout" ? " · Wyscout" : ""}`;
    if (h !== head) { ul.append(make("li", "grp", h)); head = h; }
    const li = make("li"), b = make("button");
    const k = S.teams.indexOf(t.i);
    b.setAttribute("aria-pressed", k >= 0);
    const sw = make("span", "sw"); if (k >= 0) sw.style.background = SLOT[k];
    const nm = make("span", "nm", t.team);
    b.append(sw, nm, make("span", "val", pct(t.top2)));
    b.title = `${t.label}: top two players involved in ${pct(t.top2)} of the danger`;
    b.onclick = () => toggleTeam(t.i);
    li.append(b); ul.append(li);
  }
}

function toggleTeam(i) {
  const k = S.teams.indexOf(i);
  if (k >= 0) S.teams.splice(k, 1);
  else { if (S.teams.length >= 4) S.teams.pop(); S.teams.push(i); S.focus = i; }
  if (!S.teams.includes(S.focus)) S.focus = S.teams[0] ?? null;
  teamList(); drawTeams();
}

function sentence(t, P) {
  const two = t.cov["2"][1].map(name).join(" and "), n = Math.max(1, P.length - 1);
  const frac = (f) => pct(P.filter((u) => u !== t && f(u)).length / n);
  return [`${two} were involved in ${pct(t.top2)} of the danger. ${frac((u) => u.top2 < t.top2)} of the team-seasons shown depend less on their top two.`,
    `Every chance involved at least one of ${t.tau} players; ${frac((u) => u.tau > t.tau)} of team-seasons need more players to cover all their chances.`,
    `${t.nu} chances had no player in common (separate routes); ${frac((u) => u.nu < t.nu)} of team-seasons have fewer.`,
    `${t.matches} matches, ${t.m} chances, ${fx(t.xg_per_match, 2)} open-play xG a match.`];
}

function drawTeams() {
  const P = pool(), sel = S.teams.map((i) => TS[i]);
  const cards = $("team-cards");
  cards.replaceChildren();
  if (!sel.length) cards.append(make("p", "empty", "Pick a team-season from the list to see how its attack works."));
  sel.forEach((t, k) => {
    const c = make("div", "card"); c.style.setProperty("--c", SLOT[k]);
    const b = make("button", "cardh", t.label); b.onclick = () => { S.focus = t.i; drawTeams(); };
    c.append(b, ...sentence(t, P).map((s) => make("p", null, s)));
    cards.append(c);
  });
  // coverage curve
  const B = [1, 2, 3, 4, 5];
  plot("team-curve", sel.flatMap((t, k) => [{
    x: B, y: B.map((b) => t.cov[b][0]), mode: "lines+markers", name: t.label, line: { color: SLOT[k], width: 2 }, marker: { size: 8, color: SLOT[k] },
    customdata: B.map((b) => t.cov[b][1].map(name).join(", ")), hovertemplate: `<b>%{y:.0%}</b> ${t.team}<br>%{customdata}<extra></extra>`,
  }]), { showlegend: sel.length > 0, legend: { orientation: "h", y: 1.15, x: 0 }, margin: { t: 48, r: 24, b: 52, l: 60 },
    xaxis: { title: { text: "number of players" }, dtick: 1, range: [0.8, 5.2] }, yaxis: { title: { text: "share of the team's danger they were involved in" }, tickformat: ".0%", range: [0, 1.02] } });
  // strips: every team-season in the filter, selected ones coloured and labelled
  for (const k of ["top2", "tau", "nu"]) {
    const M = MEASURE[k], jit = (t) => ((t.i * 37) % 11) / 11 - 0.5;
    plot(`strip-${k}`, [
      { x: P.map(M.get), y: P.map(jit), mode: "markers", marker: { color: T.context, size: 7, opacity: 0.6 }, text: P.map((t) => t.label),
        hovertemplate: `<b>%{x}</b> %{text}<extra></extra>` },
      ...sel.map((t, j) => ({ x: [M.get(t)], y: [jit(t)], mode: "markers+text", text: [`${t.team} ${t.season}`], textposition: j % 2 ? "bottom center" : "top center",
        textfont: { color: T.text, size: 12 }, marker: { color: SLOT[j], size: 14, line: { color: T.bg, width: 2 } },
        hovertemplate: `<b>${M.fmt(M.get(t))}</b> ${t.label}<extra></extra>`, cliponaxis: false })),
    ], { height: 130, margin: { t: 24, r: 16, b: 40, l: 16 }, xaxis: { title: { text: M.label }, ...(k === "top2" ? { tickformat: ".0%" } : { dtick: 1 }) },
      yaxis: { visible: false, range: [-0.9, 1.1] } });
  }
  $("strip-h").textContent = `Where the selected teams sit among the ${P.length} team-seasons shown`;
  drawHistory(sel);
  // combinations of the focused team-season
  const f = TS[S.focus];
  const tb = $("combo-table");
  tb.replaceChildren();
  $("combo-h").textContent = f ? `Most dangerous combinations: ${f.label}` : "Most dangerous combinations";
  if (!f) return;
  const h = tb.insertRow();
  for (const c of ["Last players involved before the shot", "Chances", "xG"]) h.append(make("th", null, c));
  for (const [Pp, n, x] of [...f.groups].sort((a, b) => b[2] - a[2]).slice(0, 12)) {
    const r = tb.insertRow();
    r.insertCell().textContent = Pp.map(name).join(", ");
    const c1 = r.insertCell(); c1.textContent = n; c1.className = "num";
    const c2 = r.insertCell(); c2.textContent = fx(x); c2.className = "num";
  }
}

function drawHistory(sel) {
  const M = MEASURE[S.measure];
  const tr = [];
  const seen = new Set();
  sel.forEach((t, k) => {
    if (seen.has(t.team)) return;
    seen.add(t.team);
    const H = TS.filter((u) => u.team === t.team && u.gender === t.gender).sort((a, b) => a.yr - b.yr || a.comp.localeCompare(b.comp));
    tr.push({ x: H.map((u) => `${u.season}${u.intl ? " " + u.comp.replace("FIFA ", "").replace("UEFA ", "") : ""}${u.source === "Wyscout" ? " (W)" : ""}`), y: H.map(M.get), mode: "lines+markers", name: t.team,
      line: { color: SLOT[k], width: 2 }, marker: { size: 9, color: SLOT[k] }, text: H.map((u) => `${u.comp} ${u.season}: ${u.cov["2"][1].map(name).join(", ")}`),
      hovertemplate: `<b>%{y}</b> ${t.team}<br>%{text}<extra></extra>` });
  });
  plot("team-history", tr, { showlegend: tr.length > 0, legend: { orientation: "h", y: 1.15, x: 0 }, margin: { t: 48, r: 24, b: 80, l: 60 },
    xaxis: { title: { text: "season or tournament" }, type: "category", tickangle: -30 },
    yaxis: { title: { text: M.label }, tickformat: S.measure === "top2" ? ".0%" : "d" } });
  const n = tr.reduce((s, t) => s + t.x.length, 0);
  $("history-note").textContent = !sel.length ? "Pick a team to see its history." : n === tr.length
    ? "The open data holds only one measured season for these teams." : "Each point is one season or tournament in which the team played at least 5 matches.";
}

// ------------------------------------------------------------------ players
const PL = [];   // one entry per player per team-season: p player, t team-season, x xG involved, n chances, s share
TS.forEach((t) => { for (const [p, [x, n]] of t.inv) PL.push({ p, t: t.i, x, n, s: x / t.xg, key: `${p}|${t.i}`, nm: name(p) }); });
const PK = Object.fromEntries(PL.map((e) => [e.key, e]));

function playerList() {
  const q = S.pq.toLowerCase(), only = $("player-only").checked;
  const rows = PL.filter((e) => pass(TS[e.t]) && (!only || S.teams.includes(e.t)) && e.n >= 3 &&
    (!q || e.nm.toLowerCase().includes(q) || TS[e.t].label.toLowerCase().includes(q))).sort((a, b) => b.s - a.s);
  const ul = $("player-list");
  ul.replaceChildren();
  if (!rows.length) { ul.append(make("li", "empty", "No player matches the search and filters.")); return; }
  for (const e of rows.slice(0, 150)) {
    const t = TS[e.t], k = S.players.indexOf(e.key), li = make("li"), b = make("button");
    b.setAttribute("aria-pressed", k >= 0);
    const sw = make("span", "sw"); if (k >= 0) sw.style.background = SLOT[k];
    const nm = make("span", "nm", e.nm); nm.append(make("span", "sub", `${t.team}, ${t.comp} ${t.season}`));
    b.append(sw, nm, make("span", "val", pct(e.s)));
    b.onclick = () => togglePlayer(e.key);
    li.append(b); ul.append(li);
  }
  if (rows.length > 150) ul.append(make("li", "empty", `${rows.length - 150} more: refine the search.`));
}

function togglePlayer(key) {
  const k = S.players.indexOf(key);
  if (k >= 0) S.players.splice(k, 1);
  else { if (S.players.length >= 6) S.players.pop(); S.players.push(key); S.pfocus = key; }
  if (!S.players.includes(S.pfocus)) S.pfocus = S.players.at(-1) ?? null;
  playerList(); drawPlayers();
}

function drawPlayers() {
  const sel = S.players.map((k) => PK[k]).filter(Boolean);
  // together, per team-season
  const by = new Map();
  for (const e of sel) by.set(e.t, [...(by.get(e.t) || []), e.p]);
  $("player-together").textContent = [...by.entries()].filter(([, P]) => P.length > 1)
    .map(([t, P]) => `Together, ${P.map(name).join(", ")} were involved in ${pct(covered(new Set(P), TS[t].groups))} of ${TS[t].label}'s danger.`).join(" ") ||
    (sel.length ? "Pick two or more players from the same team-season to see their combined share." : "Pick players from the list.");
  const lab = (e) => `${e.nm} · ${TS[e.t].team} ${TS[e.t].season}`;
  plot("player-bars", [{ y: sel.map(lab), x: sel.map((e) => e.s), type: "bar", orientation: "h", marker: { color: sel.map((_, i) => SLOT[i]) },
    text: sel.map((e) => `${pct(e.s)} · ${e.n} chances`), textposition: "outside", cliponaxis: false,
    hovertemplate: "<b>%{x:.0%}</b> of the team's danger<br>%{y}<extra></extra>" }],
  { height: Math.max(160, 48 * sel.length + 60), margin: { t: 8, r: 120, b: 44, l: 16 }, xaxis: { title: { text: "share of the team's open-play xG they were involved in" }, tickformat: ".0%", range: [0, 1] },
    yaxis: { autorange: "reversed", automargin: true } });
  // career of the focused player
  const f = PK[S.pfocus];
  $("career-h").textContent = f ? `${f.nm} across seasons and tournaments` : "Across seasons and tournaments";
  const C = f ? PL.filter((e) => e.p === f.p).sort((a, b) => TS[a.t].yr - TS[b.t].yr) : [];
  plot("player-career", [{ x: C.map((e) => `${TS[e.t].season} ${TS[e.t].team}${TS[e.t].source === "Wyscout" ? " (W)" : ""}`), y: C.map((e) => e.s), mode: "lines+markers", line: { color: T.accent, width: 2 },
    marker: { size: 9, color: T.accent }, text: C.map((e) => `${TS[e.t].label}: ${e.n} chances`), hovertemplate: "<b>%{y:.0%}</b><br>%{text}<extra></extra>" }],
  { height: 300, margin: { t: 16, r: 24, b: 90, l: 60 }, xaxis: { type: "category", tickangle: -30 }, yaxis: { title: { text: "share of the team's danger" }, tickformat: ".0%", rangemode: "tozero" } });
  $("career-note").textContent = !f ? "" : C.length > 1 ? `Measured in ${C.length} team-seasons of the open data.` : "The open data measures this player in one team-season only.";
  // partners of the focused player in that team-season
  $("partner-h").textContent = f ? `Who ${f.nm} created chances with (${TS[f.t].team}, ${TS[f.t].season})` : "Who they create chances with";
  const sh = new Map();
  if (f) for (const [P, , x] of TS[f.t].groups) if (P.includes(f.p)) for (const q of P) if (q !== f.p) sh.set(q, (sh.get(q) || 0) + x);
  const top = [...sh.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
  $("partner-note").textContent = f ? `${f.nm} was involved in ${f.n} chances worth ${fx(f.x, 1)} xG. Bars: share of that xG in which the teammate was also involved.` : "";
  plot("partner-bars", [{ y: top.map(([q]) => name(q)), x: top.map(([, x]) => x / f.x), type: "bar", orientation: "h", marker: { color: T.accent },
    text: top.map(([, x]) => pct(x / f.x)), textposition: "outside", cliponaxis: false, hovertemplate: "<b>%{x:.0%}</b> of the chances also involved %{y}<extra></extra>" }],
  { height: Math.max(160, 34 * top.length + 60), margin: { t: 8, r: 64, b: 44, l: 16 }, xaxis: { tickformat: ".0%", range: [0, 1], title: { text: "share of the player's danger shared with this teammate" } },
    yaxis: { autorange: "reversed", automargin: true } });
  // ratings (2015/16 leagues only)
  const R = (D.lineup && D.lineup.ratings) || {}, tb = $("player-ratings");
  tb.replaceChildren();
  const h = tb.insertRow();
  for (const c of ["Player", "First half (xG/90)", "Second half (xG/90)", "Minutes"]) h.append(make("th", null, c));
  for (const e of sel) {
    const r = R[String(e.p)], row = tb.insertRow();
    row.insertCell().textContent = e.nm;
    if (r) for (const v of [fx(r[0], 3), fx(r[1], 3), `${Math.round(r[2])} + ${Math.round(r[3])}`]) { const c = row.insertCell(); c.textContent = v; c.className = "num"; }
    else { const c = row.insertCell(); c.colSpan = 3; c.textContent = "Not rated: ratings exist only for 2015/16 league players with enough minutes on and off."; c.className = "note"; }
  }
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


function drawDefComp() {
  const R = (DF.by_competition || []).filter((c) => {
    const g = COMP[c.key] && COMP[c.key].gender;
    return S.gender === "all" || g === S.gender;
  }).sort((a, b) => b.entry_rate - a.entry_rate);
  const role = { train: " (model fitted)", test: " (model tested)", descriptive: "" };
  const y = R.map((c) => `${c.label}${role[c.role]}`);
  plot("def-comp", [
    { y, x: R.map((c) => c.entry_rate), type: "bar", orientation: "h", name: "Observed", marker: { color: T.accent },
      customdata: R.map((c) => [c.passes, c.matches, c.hole_median]), hovertemplate: "<b>%{x:.1%}</b> observed<br>%{y}<br>%{customdata[0]} passes, %{customdata[1]} matches<br>median hole %{customdata[2]:.1f} m<extra></extra>" },
    { y, x: R.map((c) => c.predicted), type: "bar", orientation: "h", name: "Model prediction", marker: { color: T.context },
      hovertemplate: "<b>%{x:.1%}</b> predicted by the model<br>%{y}<extra></extra>" },
  ], { barmode: "group", showlegend: true, legend: { orientation: "h", y: 1.06, x: 0 }, height: Math.max(260, 46 * R.length + 80),
    margin: { t: 40, r: 24, b: 48, l: 16 }, xaxis: { title: { text: "share of opponent-half passes followed by a box entry within 10 s" }, tickformat: ".0%" }, yaxis: { autorange: "reversed", automargin: true } });
}

// ------------------------------------------------------------------ findings
const A = D.attack;
const HM = { tau: ["Players needed so every chance involves one of them", "d"], nu: ["Separate routes (chances with no player in common)", "d"], top2: ["Share of danger involving the top two", ".0%"] };

function drawStable() {
  const rows = A.halves, k = S.metric, f = HM[k];
  const jit = (s) => (k === "top2" ? 0 : ((s.length * 13) % 9 - 4) * 0.05);
  const x = rows.map((r) => r.train[k] + jit(r.team)), y = rows.map((r) => r.test[k] + jit(r.team + "x"));
  const lo = Math.min(...x, ...y), hi = Math.max(...x, ...y);
  plot("stable-chart", [
    { x: [lo, hi], y: [lo, hi], mode: "lines", line: { color: T.context, width: 1, dash: "dot" }, hoverinfo: "skip" },
    { x, y, mode: "markers", marker: { color: T.accent, size: 9, line: { color: T.bg, width: 2 } }, text: rows.map((r) => `${r.team} (${r.league})`),
      customdata: rows.map((r) => [r.train[k], r.test[k]]), hovertemplate: `<b>%{customdata[0]${k === "top2" ? ":.0%" : ""}} → %{customdata[1]${k === "top2" ? ":.0%" : ""}}</b><br>%{text}<extra></extra>` },
  ], { xaxis: { title: { text: `${f[0]}, first half of 2015/16` }, tickformat: f[1] }, yaxis: { title: { text: "second half" }, tickformat: f[1] } });
  const r = A.H1[{ tau: "tau", nu: "nu", top2: "cov2" }[k]];
  $("stable-take").textContent = `Correlation between the two halves: ${fx(r[0])} (95% interval ${ci(r)}), 80 teams. It is a property of the team, not chance.`;
  const P = D.s2s[k];
  plot("s2s-chart", [
    { x: [Math.min(...P.pairs.map((p) => p[2])), Math.max(...P.pairs.map((p) => p[2]))], y: [Math.min(...P.pairs.map((p) => p[2])), Math.max(...P.pairs.map((p) => p[2]))], mode: "lines", line: { color: T.context, width: 1, dash: "dot" }, hoverinfo: "skip" },
    { x: P.pairs.map((p) => p[2] + (k === "top2" ? 0 : jit(p[0]))), y: P.pairs.map((p) => p[3] + (k === "top2" ? 0 : jit(p[1]))), mode: "markers",
      marker: { color: T["accent-2"], size: 9, line: { color: T.bg, width: 2 } }, text: P.pairs.map((p) => `${p[0]}: ${p[1]}`),
      customdata: P.pairs.map((p) => [p[2], p[3]]), hovertemplate: `<b>%{customdata[0]${k === "top2" ? ":.0%" : ""}} → %{customdata[1]${k === "top2" ? ":.0%" : ""}}</b><br>%{text}<extra></extra>` },
  ], { xaxis: { title: { text: `${f[0]}, one season` }, tickformat: f[1] }, yaxis: { title: { text: "the team's next season" }, tickformat: f[1] } });
  const up = P.rho && P.rho[1][0] > 0, down = P.rho && P.rho[1][1] < 0;
  $("s2s-h").textContent = up ? "From one season to the next, the pattern also carries over"
    : down ? "From one season to the next, the pattern reverses" : "From one season to the next, the pattern does not clearly carry over";
  $("s2s-take").textContent = P.rho ? `Correlation from one season to the next: ${fx(P.rho[0])} (95% interval ${ci(P.rho)}), ${P.pairs.length} pairs of consecutive seasons in ${P.comps.join(", ")}` +
      (up || down ? "." : ": not distinguishable from no relation. Within a season the shape holds (above); across a summer of transfers and coaching changes, these few pairs do not show it.")
    : `${P.pairs.length} pairs: too few for a correlation.`;
}

function drawMissing() {
  const h = A.H3.bottleneck, rows = h.teams, nu = Object.fromEntries(A.halves.map((r) => [r.team, r.train.nu]));
  plot("missing-chart", [{ x: rows.map((r) => nu[r[0]]), y: rows.map((r) => r[4]), mode: "markers", marker: { color: T.accent, size: 10, line: { color: T.bg, width: 2 } },
    text: rows.map((r) => `${r[0]}: ${name(r[5]) || r[1]} missed ${r[2]}, started ${r[3]}`), hovertemplate: "<b>%{y:.0%} less xG</b><br>%{text}<extra></extra>" }],
  { xaxis: { title: { text: "separate routes in the first half" } }, yaxis: { title: { text: "drop in xG when the player was missing" }, tickformat: ".0%" } });
  const r = h.rho_nu;
  $("missing-take").textContent = r ? `Correlation ${fx(r[0])} (95% interval ${ci(r)}), ${rows.length} teams: the expected direction, but not resolved.` : "";
}

function drawSequence() {
  const q = D.sequence;
  if (!q) { $("seq-h").hidden = true; return; }
  const rows = [["What happens and where (action type, location, movement)", "d20"], ["Which players and which passes", "d10"], ["Pass patterns between players", "d31"],
    ["Players and passes, once actions are known", "d42"], ["The exact group of players, once everything else is known", "d54"]];
  plot("seq-chart", [{ y: rows.map((r) => r[0]), x: rows.map((r) => -1000 * q[r[1]][0]), type: "bar", orientation: "h", marker: { color: rows.map((r) => (r[1] === "d20" ? T.accent : T.context)) },
    error_x: { type: "data", symmetric: false, array: rows.map((r) => 1000 * (q[r[1]][0] - q[r[1]][1][0])), arrayminus: rows.map((r) => 1000 * (q[r[1]][1][1] - q[r[1]][0])), color: T.muted },
    hovertemplate: "<b>%{x:.2f}</b><br>%{y}<extra></extra>" }],
  { height: 300, margin: { t: 8, r: 24, b: 52, l: 16 }, xaxis: { title: { text: "improvement in predicting a shot (log loss ×1000, second half); bars cross 0 = no help" }, zeroline: true }, yaxis: { autorange: "reversed", automargin: true } });
  $("seq-h").textContent = q.H4.holds ? "Who is on the ball predicts a shot beyond what they do" : "What happens and where predicts a shot; who is on the ball adds nothing";
  $("seq-note").textContent = `${(q.n.train + q.n.test).toLocaleString()} possessions still alive after three on-ball actions, 2015/16; ${pct(q.rate.test, 1)} went on to an open-play shot.`;
}

function drawProviders() {
  const P = D.providers, W = D.wyscout;
  if (!P || !W) { $("providers").hidden = true; return; }
  plot("prov-chart", [
    { x: [0.4, 1], y: [0.4, 1], mode: "lines", line: { color: T.context, width: 1, dash: "dot" }, hoverinfo: "skip" },
    { x: P.rows.map((r) => r[1]), y: P.rows.map((r) => r[2]), mode: "markers+text", text: P.rows.map((r) => r[0]), textposition: "top center",
      textfont: { size: 11, color: T["text-2"] }, marker: { color: T.accent, size: 10, line: { color: T.bg, width: 2 } },
      hovertemplate: "<b>%{x:.0%} vs %{y:.0%}</b><br>%{text}<extra></extra>" }],
  { xaxis: { title: { text: "top-two share, StatsBomb data" }, tickformat: ".0%" }, yaxis: { title: { text: "top-two share, Wyscout data" }, tickformat: ".0%" } });
  const chk = Object.entries(W.xg_check).map(([k, c]) => `${COMP[k].competition} ${COMP[k].season}: ${Math.round(c.predicted)} predicted vs ${c.open_play_goals} goals`).join("; ");
  $("prov-take").textContent = `${P.rows.length} national teams measured in both sources at the 2018 World Cup. Rank agreement: top-two share ${fx(P.rho_top2)}, players needed ${fx(P.rho_tau)}. ` +
    `Wyscout has no xG, so its chances are weighted by a model fitted on ${W.xg_model.shots.toLocaleString()} StatsBomb shots (distance, angle, header). Its goal totals: ${chk}. ` +
    "A uniform under- or over-estimate leaves every share and the player counts unchanged; only xG per match is affected.";
}

// ------------------------------------------------------------------ wiring
function redraw() { drawFilters(); teamList(); drawTeams(); playerList(); drawPlayers(); if (DF) drawDefComp(); }

function facts() {
  const F = [[String(TS.length), `team-seasons measured across ${D.seasons.competitions.filter((c) => c.measured).length} competitions and seasons, from two data providers`], [fx(A.H1.tau[0]), "how strongly a team's attacking shape repeats between half-seasons"],
    ["+" + fx(100 * A.H2.T_minus_U[0], 1) + " pts", "more later danger found by the chance-based player sets than by touches"]];
  if (DF) F.push([pct(DF.rate.test), "of opponent-half passes reach the box within 10 s"]);
  $("facts").replaceChildren(...F.map(([v, l]) => { const d = make("div"); d.append(make("b", null, v), make("span", null, l)); return d; }));
}

facts();
$("team-q").oninput = (e) => { S.q = e.target.value; teamList(); };
$("player-q").oninput = (e) => { S.pq = e.target.value; playerList(); };
$("player-only").onchange = playerList;
seg("c-measure", Object.keys(MEASURE), Object.values(MEASURE).map((m) => m.label), () => S.measure, (v) => { S.measure = v; drawHistory(S.teams.map((i) => TS[i])); });
seg("c-metric", Object.keys(HM), Object.values(HM).map((m) => m[0]), () => S.metric, (v) => { S.metric = v; drawStable(); });
const pick = (team, comp, season) => TS.find((t) => t.team === team && t.comp === comp && t.season === season);
for (const t of [pick("Barcelona", "La Liga", "2015/2016"), pick("Leicester City", "Premier League", "2015/2016"), pick("Arsenal WFC", "FA Women's Super League", "2020/2021")].filter(Boolean)) S.teams.push(t.i);
if (!S.teams.length) S.teams.push(...[...TS].sort((a, b) => b.xg - a.xg).slice(0, 3).map((t) => t.i));
S.focus = S.teams[0] ?? null;
const bar = S.teams.length ? TS[S.teams[0]] : null;
if (bar) for (const e of PL.filter((e) => e.t === bar.i).sort((a, b) => b.s - a.s).slice(0, 3)) S.players.push(e.key);
S.pfocus = S.players[0] ?? null;
if (DF) {
  $("b-compact").onclick = () => { DS.P = BLOCKS.compact.map((p) => p.slice()); drawDefence(); };
  $("b-stretch").onclick = () => { DS.P = BLOCKS.stretch.map((p) => p.slice()); drawDefence(); };
  $("b-hole").onclick = () => { DS.P = BLOCKS.hole.map((p) => p.slice()); drawDefence(); };
  seg("c-dmeasure", ["hole", "gap", "h1"], ["Largest empty circle", "Widest gap", "Topology h1"], () => S.dm, (v) => { S.dm = v; drawDefQ(); });
  drawDefence(); defCheck(); drawDefQ(); drawDefGain();
}
redraw(); drawStable(); drawMissing(); drawSequence(); drawProviders();
$("cov-check").textContent = covOK ? `Coverage check passed: the browser reproduces the published best-set coverage for all ${TS.length} team-seasons (largest difference ${covErr.toExponential(1)}).`
  : "Coverage check FAILED: the browser and Python disagree.";
$("cov-check").className = "note " + (covOK ? "ok" : "warn");
