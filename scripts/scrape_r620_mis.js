/* =====================================================================================
 * scrape_r620_mis.js — R6.20 tab 4 (NRM / Water / All Plantation Works), all FY, all blocks.
 *
 * This runs in the BROWSER, not in Node. The MGNREGA MIS is behind an arithmetic CAPTCHA and the
 * report is an ASP.NET WebForms page driven by __doPostBack against a live __VIEWSTATE, so there is
 * no URL that returns the data and no way to do this from a shell. The workspace cannot reach
 * mnregaweb4.dord.gov.in at all.
 *
 * HOW TO RUN
 *   1. Open https://mnregaweb4.dord.gov.in/netnregarep/MISreport4.aspx and clear the CAPTCHA
 *      yourself. (Do not ask an agent to do this; it is a bot gate.)
 *   2. Navigate: R6.20 -> tab 4 "NRM/Water/All Plantation Works" -> state ODISHA. You should be on
 *      Progress_Maintenance_Frame.aspx with the report in an iframe.
 *   3. Paste this whole file into the devtools console, then:  await R620.runAll()
 *   4. R620.csv() returns the 1170-row district CSV; R620.totalsCsv() the 39 printed Total rows.
 *      Copy both out and drop them in 00_raw/mis_reports/, then run scripts/verify_r620.py.
 *
 * Re-scraping later will NOT reproduce the old numbers for every year, and that is correct
 * behaviour: FY2020-21 onward is restated continuously (see docs/DATA_NOTES.md). Keep the dated
 * copy in 00_raw/ as the citable one and let verify_r620.py tell you what moved.
 *
 * TWO TRAPS, both handled below. Both produced plausible-looking wrong data first.
 *   (1) The block selector defaults to MWC-Block — ONE block. Left alone the report silently returns
 *       9 blocks of Odisha and looks like a normal small state. "ALL" is Rbblk value "0" at radio
 *       INDEX 4. The index and the value disagree; trust the value.
 *   (2) ASP.NET posts the radio value from the DOM, so calling __doPostBack without first setting
 *       .checked = true posts the PREVIOUS selection. Symptom: all three categories come back
 *       identical and every table is stamped with the same Rbblk. It does not throw.
 * ===================================================================================== */
window.R620 = (function () {
  "use strict";

  const CATEGORIES = ["NRM", "Water", "Plantation"];   // RadioButtonList2 values 0,1,2 in this order
  const FYS = ["2014-2015", "2015-2016", "2016-2017", "2017-2018", "2018-2019", "2019-2020",
               "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026",
               "2026-2027"];
  const COLNUM = /^[\d=/*+.\s-]+$/;                    // the "1 2 3 ... 9=7/8*100" row under the header
  const out = {};                                      // out[fy][category] = {header,rows,total,...}
  let tpl = null;                                      // inner report URL with fin_year to substitute

  const frame = () => {
    const f = document.querySelector("iframe, frame");
    if (!f) throw new Error("no iframe — are you on Progress_Maintenance_Frame.aspx?");
    return f;
  };

  const frameLoad = (f) => new Promise((res, rej) => {
    const t = setTimeout(() => rej(new Error("frame load timed out after 60s")), 60000);
    f.addEventListener("load", function h() {
      f.removeEventListener("load", h); clearTimeout(t); setTimeout(res, 400);
    });
  });

  /* A cell with rowspan/colspan is written into its FIRST row only; the cells it covers are marked
     occupied and left blank, so column indices stay aligned across the whole table. Same algorithm
     as grid() in parse_mis_html_reports.py — keep the two in step. */
  function grid(table) {
    const occ = new Map(), key = (r, c) => r + ":" + c;
    const trs = [...table.querySelectorAll("tr")];
    trs.forEach((tr, r) => {
      let c = 0;
      for (const td of tr.children) {
        while (occ.has(key(r, c))) c++;
        const txt = (td.textContent || "").replace(/\s+/g, " ").trim();
        const rs = Math.max(1, td.rowSpan || 1), cs = Math.max(1, td.colSpan || 1);
        for (let dr = 0; dr < rs; dr++)
          for (let dc = 0; dc < cs; dc++)
            occ.set(key(r + dr, c + dc), dr === 0 && dc === 0 ? txt : "");
        c += cs;
      }
    });
    let nr = 0, nc = 0;
    for (const k of occ.keys()) {
      const [r, c] = k.split(":").map(Number);
      nr = Math.max(nr, r + 1); nc = Math.max(nc, c + 1);
    }
    return Array.from({ length: nr }, (_, r) =>
      Array.from({ length: nc }, (_, c) => occ.get(key(r, c)) ?? ""));
  }

  /* The Total row is printed BOTH above and below the data, with its serial cell blank — so the
     label "Total" lands in column 1, not column 0. Check both. */
  const isTotal = (row) => row.slice(0, 2).some((v) => (v || "").trim().toLowerCase() === "total");
  const isColnum = (row) => {
    const cells = row.map((v) => (v || "").trim()).filter(Boolean);
    return cells.length >= 3 && cells.every((c) => COLNUM.test(c));
  };

  function parse(doc) {
    const tables = [...doc.querySelectorAll("table")]
      .map((t) => ({ t, g: grid(t) }))
      .filter(({ g }) => g.some(isTotal) && g.length > 5);
    if (!tables.length) throw new Error("no data table with a Total row found");
    const g = tables.sort((a, b) => b.g.length - a.g.length)[0].g;

    const total = g.find(isTotal);
    const header = g.find((r) => r.some((v) => /District/i.test(v || ""))) || [];
    const rows = g.filter((r) => {
      if (isTotal(r) || isColnum(r) || r === header) return false;
      const name = (r[1] || "").trim();
      return name && !/District|S\s*No/i.test(name) && r.filter(Boolean).length >= 6;
    });

    const lu = (doc.body.textContent.match(/[Ll]ast\s*[Uu]pdated?\s*[:\-]?\s*(\d{2}\/\d{2}\/\d{4})/) || [])[1] || "";
    return { header, rows, total, lastUpdated: lu, nRows: rows.length };
  }

  /* Set .checked FIRST, then post. Trap (2). */
  async function setAndPost(f, name, value, idx) {
    const d = f.contentDocument;
    const rs = [...d.querySelectorAll("input[type=radio]")].filter((x) => x.name.includes(name));
    const target = rs.find((x) => x.value === value);
    if (!target) throw new Error(`${name}: no radio with value "${value}" (saw ${rs.map(r=>r.value)})`);
    rs.forEach((x) => { x.checked = false; });
    target.checked = true;
    const p = frameLoad(f);
    f.contentWindow.__doPostBack(`ctl00$ContentPlaceHolder1$${name}$${idx}`, "");
    await p;
    const still = [...f.contentDocument.querySelectorAll("input[type=radio]")]
      .filter((x) => x.name.includes(name) && x.checked).map((x) => x.value);
    if (!still.includes(value))
      throw new Error(`${name}: posted "${value}" but page came back with "${still}" — trap (2)`);
  }

  async function pull(fy) {
    const f = frame();
    if (!tpl) {
      tpl = f.src;
      if (!/fin_year=\d{4}-\d{4}/.test(tpl))
        throw new Error("iframe src has no fin_year= — wrong page, or navigate to the report first");
    }
    const p0 = frameLoad(f);
    f.src = tpl.replace(/fin_year=\d{4}-\d{4}/, "fin_year=" + fy);
    await p0;

    await setAndPost(f, "Rbblk", "0", 4);              // ALL blocks. Trap (1): value 0, index 4.
    const res = {};
    for (let cat = 0; cat < 3; cat++) {
      await setAndPost(f, "RadioButtonList2", String(cat), cat);
      const got = parse(f.contentDocument);
      if (got.nRows !== 30)
        console.warn(`${fy} ${CATEGORIES[cat]}: ${got.nRows} district rows, expected 30`);
      res[CATEGORIES[cat]] = got;
    }
    // trap (2) again, at the data level: three identical tables means the posts did not take
    const sig = CATEGORIES.map((c) => JSON.stringify(res[c].total));
    if (new Set(sig).size === 1)
      throw new Error(`${fy}: all three categories returned identical totals — trap (2)`);
    return res;
  }

  async function runAll(fys) {
    for (const fy of (fys || FYS)) {
      try { out[fy] = await pull(fy); console.log(`${fy} ok`); }
      catch (e) { console.error(`${fy} FAILED: ${e.message}`); }
    }
    const done = Object.keys(out).length;
    console.log(`${done}/${(fys||FYS).length} years; R620.csv() and R620.totalsCsv() to export`);
    return done;
  }

  const num = (v) => (v || "").replace(/,/g, "").trim();

  function csv() {
    const L = ["fy,category,district,blocks,works_ongoing,works_completed,pct_works,exp_cat_lakh,exp_all_lakh,pct_exp"];
    for (const fy of FYS) {
      if (!out[fy]) continue;
      for (const c of CATEGORIES)
        for (const r of out[fy][c].rows)
          L.push([fy, c, r[1], ...r.slice(2, 9).map(num)].join(","));
    }
    return L.join("\n");
  }

  function totalsCsv() {
    const L = ["fy,category,blocks,works_ongoing,works_completed,pct_works,exp_cat_lakh,exp_all_lakh,pct_exp,last_updated"];
    for (const fy of FYS) {
      if (!out[fy]) continue;
      for (const c of CATEGORIES) {
        const s = out[fy][c];
        L.push([fy, c, ...s.total.slice(2, 9).map(num), s.lastUpdated].join(","));
      }
    }
    return L.join("\n");
  }

  return { runAll, pull, csv, totalsCsv, out, FYS, CATEGORIES };
})();
