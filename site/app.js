/* Trading Agent dashboard - renders data.json built by scripts/dashboard.py. No secrets, no API calls. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = (x, d = 2) => (x == null || isNaN(x)) ? "n/a" : (x >= 0 ? "+" : "") + (x * 100).toFixed(d) + "%";
  const pctAbs = (x, d = 1) => (x == null || isNaN(x)) ? "n/a" : (x * 100).toFixed(d) + "%";
  const usd = (x) => (x == null || isNaN(x)) ? "n/a" : "$" + Number(x).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const signCls = (x) => x == null ? "" : (x > 0 ? "pos" : x < 0 ? "neg" : "");
  const ageText = (h) => h == null ? "never" : h < 1 ? Math.round(h * 60) + " min ago" : h < 48 ? h.toFixed(1) + " h ago" : Math.round(h / 24) + " d ago";
  const etShort = (iso) => { if (!iso) return "-"; const d = new Date(iso); return d.toLocaleString("en-US", { timeZone: "America/New_York", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }); };

  // theme toggle (per-viewer convenience only)
  $("theme").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme");
    const dark = cur ? cur === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    const next = dark ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("ta_theme", next); } catch (e) { /* storage may be unavailable */ }
    render(window.__data);
  });

  function tile(label, value, delta, cls, hero) {
    const t = el("div", "tile" + (hero ? " hero" : ""));
    t.appendChild(el("div", "label", label));
    const v = el("div", "value" + (cls ? " " + cls : ""), value);
    t.appendChild(v);
    if (delta) t.appendChild(el("div", "delta", delta));
    return t;
  }
  function statusChip(text) {
    const m = { OK: "st-ok", SKIPPED: "st-skip", ABORTED: "st-abort", MISSING: "st-miss" };
    const glyph = { OK: "✓", SKIPPED: "·", ABORTED: "✕", MISSING: "!" };
    const s = el("span", "status " + (m[text] || "st-warn"));
    s.appendChild(el("i", "dot"));
    s.appendChild(document.createTextNode((glyph[text] || "") + " " + text));
    return s;
  }
  function table(headers, rows, numeric) {
    const t = el("table"); const th = el("tr");
    headers.forEach((h, i) => th.appendChild(el("th", numeric && numeric[i] ? "num" : "", h)));
    t.appendChild(el("thead")).appendChild(th);
    const tb = el("tbody");
    rows.forEach((r) => { const tr = el("tr"); r.forEach((c, i) => { const td = el("td", numeric && numeric[i] ? "num" : ""); if (c instanceof Node) td.appendChild(c); else td.textContent = c == null ? "-" : c; tr.appendChild(td); }); tb.appendChild(tr); });
    t.appendChild(tb); return t;
  }

  // ---- line chart (multi-series, one axis, crosshair tooltip, keyboard) -----------------------
  function lineChart(wrap, dates, series, opts) {
    wrap.textContent = "";
    const pts = dates.map((d, i) => ({ d, v: series.map((s) => s.values[i]) })).filter((p) => p.v.some((x) => x != null));
    if (pts.length < 2) { wrap.appendChild(el("div", "empty", opts.emptyText || "Not enough data yet.")); return; }
    const W = 900, H = opts.height || 260, m = { l: 44, r: 12, t: 10, b: 26 };
    const all = pts.flatMap((p) => p.v).filter((x) => x != null);
    let lo = Math.min(...all), hi = Math.max(...all);
    if (opts.zero) hi = Math.max(hi, 0);
    if (hi === lo) { hi += 1; lo -= 1; }
    const pad = (hi - lo) * 0.08; lo -= pad; hi += pad;
    const x = (i) => m.l + (i / (pts.length - 1)) * (W - m.l - m.r);
    const y = (v) => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("class", "chart"); svg.setAttribute("tabindex", "0");
    svg.setAttribute("role", "img"); svg.setAttribute("aria-label", opts.label || "chart");
    const g = (tag, attrs) => { const e = document.createElementNS(ns, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };
    // grid + y ticks (4 hairlines)
    for (let k = 0; k <= 4; k++) {
      const v = lo + (hi - lo) * (k / 4);
      svg.appendChild(g("line", { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), stroke: "var(--grid)", "stroke-width": 1 }));
      const t = g("text", { x: m.l - 6, y: y(v) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)", style: "font-variant-numeric: tabular-nums" });
      t.textContent = opts.fmt ? opts.fmt(v) : v.toFixed(1); svg.appendChild(t);
    }
    if (opts.zero) svg.appendChild(g("line", { x1: m.l, x2: W - m.r, y1: y(0), y2: y(0), stroke: "var(--axis)", "stroke-width": 1 }));
    // x labels: first, middle, last
    [0, Math.floor((pts.length - 1) / 2), pts.length - 1].forEach((i) => {
      const t = g("text", { x: x(i), y: H - 8, "text-anchor": i === 0 ? "start" : i === pts.length - 1 ? "end" : "middle", "font-size": 11, fill: "var(--muted)" });
      t.textContent = pts[i].d.slice(5); svg.appendChild(t);
    });
    series.forEach((s, si) => {
      let d = ""; pts.forEach((p, i) => { if (p.v[si] == null) return; d += (d ? " L" : "M") + x(i).toFixed(1) + " " + y(p.v[si]).toFixed(1); });
      svg.appendChild(g("path", { d, fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
      const last = [...pts].reverse().find((p) => p.v[si] != null);
      if (last) { const i = pts.indexOf(last); svg.appendChild(g("circle", { cx: x(i), cy: y(last.v[si]), r: 4, fill: s.color, stroke: "var(--surface)", "stroke-width": 2 })); }
    });
    const cross = g("line", { x1: 0, x2: 0, y1: m.t, y2: H - m.b, stroke: "var(--axis)", "stroke-width": 1, visibility: "hidden" });
    svg.appendChild(cross);
    const dots = series.map((s) => { const c = g("circle", { r: 5, fill: s.color, stroke: "var(--surface)", "stroke-width": 2, visibility: "hidden" }); svg.appendChild(c); return c; });
    wrap.appendChild(svg);
    const tip = el("div", "tip"); wrap.appendChild(tip);
    let idx = -1;
    function show(i) {
      idx = i; const p = pts[i];
      cross.setAttribute("x1", x(i)); cross.setAttribute("x2", x(i)); cross.setAttribute("visibility", "visible");
      tip.textContent = ""; tip.appendChild(el("div", "t", p.d));
      series.forEach((s, si) => {
        const v = p.v[si]; dots[si].setAttribute("visibility", v == null ? "hidden" : "visible");
        if (v != null) { dots[si].setAttribute("cx", x(i)); dots[si].setAttribute("cy", y(v)); }
        const row = el("div", "row"); const k = el("span"); const key = el("i", "k"); key.style.borderColor = s.color; k.appendChild(key); k.appendChild(document.createTextNode(s.name));
        row.appendChild(k); row.appendChild(el("b", "", v == null ? "n/a" : (opts.fmt ? opts.fmt(v) : v.toFixed(2)) + (s.extra ? " · " + s.extra(i) : ""))); tip.appendChild(row);
      });
      tip.style.display = "block";
      const rect = svg.getBoundingClientRect(); const px = x(i) / W * rect.width;
      tip.style.left = Math.min(Math.max(px + 12, 0), rect.width - 170) + "px"; tip.style.top = "8px";
    }
    function hide() { cross.setAttribute("visibility", "hidden"); dots.forEach((c) => c.setAttribute("visibility", "hidden")); tip.style.display = "none"; idx = -1; }
    svg.addEventListener("pointermove", (ev) => { const rect = svg.getBoundingClientRect(); const px = (ev.clientX - rect.left) / rect.width * W; const i = Math.round((px - m.l) / (W - m.l - m.r) * (pts.length - 1)); show(Math.max(0, Math.min(pts.length - 1, i))); });
    svg.addEventListener("pointerleave", hide);
    svg.addEventListener("keydown", (ev) => { if (ev.key === "ArrowLeft" || ev.key === "ArrowRight") { ev.preventDefault(); show(Math.max(0, Math.min(pts.length - 1, (idx < 0 ? pts.length - 1 : idx) + (ev.key === "ArrowRight" ? 1 : -1)))); } if (ev.key === "Escape") hide(); });
    svg.addEventListener("focus", () => show(pts.length - 1)); svg.addEventListener("blur", hide);
  }

  // ---- render --------------------------------------------------------------------------------
  function render(data) {
    if (!data) return;
    const a = data.account, n = data.news, sc = n.scorecard || {}, st = n.state || {};
    const cs = getComputedStyle(document.documentElement);
    const c1 = cs.getPropertyValue("--s1").trim(), c2 = cs.getPropertyValue("--s2").trim();
    $("sub").textContent = `${a.phase || "paper"} · account …${a.account_tail || "?"} · start ${a.start_date || "?"} at ${usd(a.start_equity)} · last EOD ${a.series.dates.slice(-1)[0] || "none yet"} · built ${data.meta.built_at_et} ET`;
    $("repo").href = data.meta.repo;

    const tiles = $("tiles"); tiles.textContent = "";
    tiles.appendChild(tile("Equity", usd(a.equity), a.day_return == null ? "day change n/a" : "day " + pct(a.day_return), "", true));
    tiles.appendChild(tile("Phase return", pct(a.phase_return), "SPY " + pct(a.spy_phase_return) + (a.phase_return != null && a.spy_phase_return != null ? " · diff " + pct(a.phase_return - a.spy_phase_return) : ""), signCls(a.phase_return)));
    tiles.appendChild(tile("Max drawdown", pctAbs(a.max_dd), "SPY " + pctAbs(a.spy_max_dd) + " · limit 8%", a.max_dd != null && a.max_dd <= -0.08 ? "neg" : ""));
    tiles.appendChild(tile("Invested", pctAbs(a.invested), "floor 70% · satellites " + pctAbs(a.sat_pct), a.invested != null && a.invested < 0.70 ? "neg" : ""));
    tiles.appendChild(tile("Cash", usd(a.cash), "regime " + (a.regime || "n/a")));
    const ks = a.ks_fail && a.ks_fail.length ? a.ks_fail.join(", ") : "none";
    tiles.appendChild(tile("Kill switches failing", ks, a.paused ? "PAUSED flag present" : "not paused", ks === "none" ? "" : "neg"));

    const s = a.series;
    lineChart($("eq-wrap"), s.dates, [
      { name: "Bot equity", color: c1, values: s.equity_idx, extra: (i) => usd(s.equity[i]) },
      { name: "SPY", color: c2, values: s.spy_idx, extra: (i) => s.spy_close[i] == null ? "" : s.spy_close[i].toFixed(2) }],
      { fmt: (v) => v.toFixed(1), label: "Bot equity and SPY indexed to 100", emptyText: s.dates.length ? "One snapshot so far (" + s.dates[0] + ", " + usd(s.equity[0]) + "). The line starts with the second EOD." : "No EOD snapshot yet." });
    lineChart($("dd-wrap"), s.dates, [
      { name: "Bot", color: c1, values: s.drawdown }, { name: "SPY", color: c2, values: s.spy_drawdown }],
      { fmt: (v) => (v * 100).toFixed(1) + "%", height: 150, zero: true, label: "Drawdown from peak", emptyText: "Drawdown appears with the second EOD." });
    $("eq-table").textContent = "";
    $("eq-table").appendChild(table(["Date", "Equity", "Equity idx", "SPY close", "SPY idx", "Invested", "Drawdown"],
      s.dates.map((d, i) => [d, usd(s.equity[i]), s.equity_idx[i] == null ? "-" : s.equity_idx[i].toFixed(2), s.spy_close[i] == null ? "-" : s.spy_close[i].toFixed(2), s.spy_idx[i] == null ? "-" : s.spy_idx[i].toFixed(2), pctAbs(s.invested[i]), pct(s.drawdown[i])]).reverse(),
      [0, 1, 1, 1, 1, 1, 1]));

    const pos = $("positions"); pos.textContent = "";
    if (!a.positions.length) pos.appendChild(el("div", "empty", "No positions. Day 1 buys the core (SPYM) at the first market-open."));
    else pos.appendChild(table(["Symbol", "Role", "Qty", "Avg", "Last", "P&L", "% equity", "Stop"],
      a.positions.map((p) => [p.sym, p.role, p.qty, p.avg == null ? "-" : p.avg.toFixed(2), p.last == null ? "-" : p.last.toFixed(2), p.plpc == null ? "-" : pct(p.plpc), p.pct == null ? "-" : pctAbs(p.pct), p.stop || "-"]), [0, 0, 1, 1, 1, 1, 1, 0]));

    const cad = $("cadence"); cad.textContent = "";
    if (!data.cadence.length) cad.appendChild(el("div", "empty", "No routine commits yet."));
    else cad.appendChild(table(["Date", "pre-market", "market-open", "midday", "eod", "weekly"],
      data.cadence.slice().reverse().map((r) => [r.date, statusChip(r["pre-market"]), statusChip(r["market-open"]), statusChip(r.midday), statusChip(r.eod), r.weekly ? statusChip(r.weekly) : "—"])));

    const gr = $("graduation"); gr.textContent = "";
    const gd = data.graduation;
    $("grad-meta").textContent = gd.week ? `week ending ${gd.week}${gd.grade ? " · grade " + gd.grade : ""}${gd.reviewed ? " · reviewed " + gd.reviewed : " · not yet reviewed by the user"}` : "";
    if (!gd.items.length) gr.appendChild(el("div", "empty", "11 criteria (TRADING-STRATEGY.md). Marks appear after the first Friday review."));
    else { const ul = el("ul", "plain"); gd.items.forEach((it) => ul.appendChild(el("li", "", it.mark + " " + it.text))); gr.appendChild(ul); }

    // news sleeve
    const nt = $("news-tiles"); nt.textContent = "";
    const stale = st.age_h == null || st.age_h > 3;
    nt.appendChild(tile("Scanner last OK", ageText(st.age_h), st.last_error ? "last error: " + String(st.last_error).slice(0, 60) : (st.more_pending ? "catching up" : "healthy cadence = every 15 min"), stale ? "neg" : ""));
    nt.appendChild(tile("Headlines stored", st.raw_total == null ? "0" : String(st.raw_total), "pending classification " + (st.pending == null ? "n/a" : st.pending)));
    const cnt = sc.counts || {};
    nt.appendChild(tile("Signals", String(cnt.signals || 0), `bull ${cnt.bull || 0} · bear ${cnt.bear || 0} · none ${cnt.none || 0} · scored ${cnt.scored || 0}`));
    nt.appendChild(tile("Classifier today", st.cost_today == null ? "$0.00" : "$" + Number(st.cost_today).toFixed(2), (st.calls_today || 0) + " calls" + (st.model ? " · " + st.model : "") + (st.classifier_note ? " · " + st.classifier_note : "")));
    const g = sc.gate;
    $("gate").textContent = g ? (g.met ? "GATE: MET — tradeable buckets exist; Phase 5 may be prepared (user decision)." : "GATE: NOT MET — " + g.reasons.join("; ") + ".") : "Scorer has not run yet (nightly). Gate rules: PLAN.md §6.";
    const up = $("uptime"); up.textContent = "";
    const bars = el("div", "bars"), labels = el("div", "barlabels");
    (n.uptime || []).forEach((d) => { const b = el("div", "b" + (d.uptime < 0.95 ? " low" : "")); b.style.height = Math.max(2, Math.round(d.uptime * 46)) + "px"; b.title = `${d.date}: ${d.runs} runs (${Math.round(d.uptime * 100)}%)`; b.setAttribute("aria-label", b.title); bars.appendChild(b); labels.appendChild(el("span", "", d.date.slice(5))); });
    up.appendChild(bars); up.appendChild(labels);
    up.appendChild(el("div", "small", (n.uptime || []).map((d) => d.date.slice(5) + " " + d.runs).join(" · ") || "no runs yet"));
    const tr = $("tradeable"); tr.textContent = "";
    if (g && g.tradeable && g.tradeable.length) tr.appendChild(table(["asset", "conf", "mag", "category", "n", "mean", "t"], g.tradeable.map((b) => [b.asset, b.conf, b.mag, b.category, b.n, pct(b.mean), b.t]), [0, 0, 0, 0, 1, 1, 1]));
    else tr.appendChild(el("div", "empty", "none yet"));
    const fmtSt = (h) => !h || !h.n ? "n=0" : `n=${h.n} · ${pct(h.mean)} · med ${pct(h.median)} · t ${h.t}`;
    const bk = $("buckets"); bk.textContent = "";
    if (!(sc.asset || []).length) bk.appendChild(el("div", "empty", "No scored signals yet. First rows appear the night after the first signal's d1 close."));
    else bk.appendChild(table(["asset", "dir", "h1 (diag.)", "d1", "d3", "d5"], sc.asset.slice().sort((p, q) => (p.asset + p.direction).localeCompare(q.asset + q.direction)).map((b) => [b.asset, b.direction, fmtSt(b.horizons.h1), fmtSt(b.horizons.d1), fmtSt(b.horizons.d3), fmtSt(b.horizons.d5)])));
    const fine = $("fine"); fine.textContent = "";
    if ((sc.fine || []).length) fine.appendChild(table(["asset", "dir", "conf", "mag", "category", "d3", "tradeable"], sc.fine.map((b) => [b.asset, b.direction, b.conf, b.mag, b.category, fmtSt(b.horizons.d3), b.tradeable ? "YES" : "no"])));
    else fine.appendChild(el("div", "empty", "none yet"));
    const fd = $("feed"); fd.textContent = "";
    if (!n.feed.length) fd.appendChild(el("div", "empty", st.classifier_note || "No signals yet."));
    else fd.appendChild(table(["time ET", "ticker", "dir", "m", "conf", "category", "d1", "d3", "headline"], n.feed.map((f) => {
      const h = f.url ? el("a", "", f.headline) : el("span", "", f.headline); if (f.url) { h.href = f.url; h.target = "_blank"; h.rel = "noopener"; }
      return [etShort(f.ts), f.ticker, f.dir, f.mag, f.conf == null ? "-" : f.conf.toFixed(2), f.cat, f.d1 == null ? "-" : pct(f.d1), f.d3 == null ? "-" : pct(f.d3), h];
    }), [0, 0, 0, 1, 1, 0, 1, 1, 0]));

    const pl = $("plan"); pl.textContent = "";
    if (!data.plan.length) pl.appendChild(el("div", "empty", "plans/news-sleeve/STATUS.md not found"));
    else { const ul = el("ul", "plain"); data.plan.forEach((p) => ul.appendChild(el("li", "", `Phase ${p.phase} ${p.title}: ${p.state}`))); pl.appendChild(ul); }
    const no = $("notes"); no.textContent = "";
    if (!data.notifications.length) no.appendChild(el("div", "empty", "none in the last 7 days"));
    else { const ul = el("ul", "plain"); data.notifications.forEach((x) => ul.appendChild(el("li", "", x.time + " — " + x.text))); no.appendChild(ul); }
    $("foot").textContent = `Built ${data.meta.built_at} from commit ${data.meta.commit || "?"}. Numbers come from scripts/ks.py, scripts/newsscan.py and scripts/newsscore.py; this page only displays them. Not financial advice.`;
  }

  fetch("data.json", { cache: "no-store" }).then((r) => r.json()).then((d) => { window.__data = d; render(d); })
    .catch((e) => { $("sub").textContent = "data.json could not be loaded: " + e; });
})();
