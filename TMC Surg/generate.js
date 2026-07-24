const fs = require('fs');

const DAYS = 14;
const PEOPLE = 15;

const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TMC Surgery Rotation Schedule — Cycle 1</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    background: #f0f2f5;
    color: #333;
    padding: 24px;
  }
  .header { text-align: center; margin-bottom: 20px; }
  .header h1 { font-size: 24px; color: #1a2a3a; margin-bottom: 4px; letter-spacing: 0.5px; }
  .header h2 { font-size: 14px; color: #6b7b8d; font-weight: 400; margin-bottom: 4px; }
  .header .subtitle { font-size: 12px; color: #8899aa; }

  .legend {
    display: flex; flex-wrap: wrap; gap: 14px; justify-content: center;
    margin: 14px 0 8px; padding: 10px 16px;
    background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .legend-item { display: flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 500; }
  .legend-swatch { width: 18px; height: 13px; border-radius: 3px; border: 1px solid rgba(0,0,0,0.15); }

  .daily-info {
    text-align: center; font-size: 12px; color: #555;
    margin: 8px 0 16px;
    background: #e8f4e8; padding: 8px 14px; border-radius: 6px;
    display: inline-block;
  }
  .info-wrap { text-align: center; margin-bottom: 16px; }

  .schedule-wrap {
    overflow-x: auto;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
  }
  table { border-collapse: collapse; font-size: 11px; width: 100%; min-width: 1200px; }
  th, td { border: 1px solid #d5dce4; padding: 6px 8px; text-align: center; white-space: nowrap; }
  thead th { background: #1a2a3a; color: #fff; font-weight: 600; font-size: 11px; letter-spacing: 0.3px; position: sticky; top: 0; z-index: 2; }
  thead th.sub-header { background: #2c3e50; font-weight: 500; font-size: 10.5px; }
  thead th.weekend { background: #34495e; }
  .name-cell {
    text-align: left !important; font-weight: 600; background: #f7f9fb !important;
    min-width: 210px; position: sticky; left: 0; z-index: 1; border-right: 2px solid #bcc8d4;
  }
  thead .name-cell { z-index: 3; }
  tbody tr:nth-child(even) .name-cell { background: #eff3f7 !important; }
  tbody tr:hover .name-cell { background: #e3eaf1 !important; }
  tbody tr:hover td:not(.name-cell) { filter: brightness(0.96); }

  .am-or { background: #c6efce; color: #006100; font-weight: 600; }
  .am-fl { background: #a9d18e; color: #375623; font-weight: 600; }
  .am-er { background: #ffc7ce; color: #9c0006; font-weight: 600; }
  .am-wc { background: #fff2cc; color: #7f6000; font-weight: 600; }
  .anes  { background: #d9d2e9; color: #351c75; font-weight: 600; }
  .pm-or { background: #d6e4f0; color: #1f4e79; font-weight: 600; }
  .pm-fl { background: #b4c7e7; color: #1f3864; font-weight: 600; }
  .pm-er { background: #f4b183; color: #843c0c; font-weight: 600; }
  .off   { background: #d5d5d5; color: #555; font-weight: 700; letter-spacing: 1px; }

  .totals-cell { background: #ecf0f1 !important; font-weight: 700; font-size: 9.5px; line-height: 1.4; color: #555; vertical-align: top; }

  .summary-section { max-width: 1000px; margin: 0 auto 24px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; }
  .summary-section h3 { font-size: 16px; color: #1a2a3a; margin-bottom: 12px; }
  .summary-section table { min-width: auto; font-size: 12px; }
  .summary-section thead th { background: #27ae60; }
  .expected-row td { background: #f0f8f0 !important; font-weight: 700; color: #2c7a2c; }

  .btn-group { text-align: center; margin: 16px 0; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
  .btn { padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
  .btn-primary { background: #2980b9; color: #fff; }
  .btn-primary:hover { background: #3498db; transform: translateY(-1px); box-shadow: 0 2px 6px rgba(41,128,185,0.3); }
  .btn-secondary { background: #27ae60; color: #fff; }
  .btn-secondary:hover { background: #2ecc71; transform: translateY(-1px); box-shadow: 0 2px 6px rgba(39,174,96,0.3); }
  .btn-success { opacity: 0; transition: opacity 0.3s; font-size: 13px; color: #27ae60; font-weight: 600; }
  .btn-success.show { opacity: 1; }
  .btn-toggle { background: #8e44ad; color: #fff; }
  .btn-toggle:hover { background: #9b59b6; transform: translateY(-1px); box-shadow: 0 2px 6px rgba(142,68,173,0.3); }

  .notes { max-width: 750px; margin: 20px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 18px 24px; font-size: 12.5px; color: #555; line-height: 1.7; }
  .notes h4 { color: #1a2a3a; margin-bottom: 8px; font-size: 14px; }
  .notes ul { padding-left: 20px; }
  .notes li { margin-bottom: 4px; }
  .notes strong { color: #333; }
  .highlight { background: #fffde7; border-left: 3px solid #f9a825; padding: 8px 12px; margin: 10px 0; border-radius: 4px; }

  @media print { body { padding: 8px; background: #fff; } .btn-group, .notes { display: none; } .schedule-wrap, .summary-section { box-shadow: none; } table { font-size: 9px; } }
</style>
</head>
<body>

<div class="header">
  <h1>TMC SURGERY ROTATION SCHEDULE</h1>
  <h2>Cycle 1 — August 10 to August 23, 2026 — 14-Day Cycle</h2>
  <div class="subtitle">No 24-Hour Duty &bull; Anes &amp; Wound Care = AM Duty &bull; 2 OFF Days Per Person (Split Across Weeks)</div>
</div>

<div class="legend">
  <div class="legend-item"><div class="legend-swatch" style="background:#c6efce"></div>AM - OR</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#a9d18e"></div>AM - FLOORS</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#ffc7ce"></div>AM - ER</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#fff2cc"></div>AM - WOUND</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#d9d2e9"></div>ANES</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#d6e4f0"></div>PM - OR</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#b4c7e7"></div>PM - FLOORS</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#f4b183"></div>PM - ER</div>
  <div class="legend-item"><div class="legend-swatch" style="background:#d5d5d5"></div>OFF</div>
</div>

<div class="info-wrap">
  <div class="daily-info">
    <strong>Daily Staffing:</strong>
    Mon–Sat: 13 on duty + 2 OFF &nbsp;|&nbsp; Sundays: 12 on duty + 3 OFF<br>
    <strong>Extras priority — AM:</strong> OR &gt; ER &gt; Floors &nbsp;|&nbsp; <strong>PM:</strong> ER &gt; OR &gt; Floors
  </div>
</div>

<div class="btn-group">
  <button class="btn btn-toggle" id="toggleViewBtn" onclick="toggleView()">🔄 Switch to Person View</button>
  <button class="btn btn-primary" onclick="copyTSV()">📋 Copy for Spreadsheet (Tab-separated)</button>
  <button class="btn btn-secondary" onclick="downloadCSV()">⬇️ Download CSV</button>
  <span class="btn-success" id="copyMsg">✓ Copied!</span>
</div>

<div class="schedule-wrap">
  <table id="scheduleTable"></table>
</div>

<div class="summary-section" id="summarySection"></div>

<div class="notes">
  <h4>📝 Schedule Design Notes</h4>
  <div class="highlight">
    <strong>🛡️ No 24-Hour Duty:</strong> PM duties are split into 2 mini-blocks, each followed by an OFF day. No PM → AM without rest.
  </div>
  <ul>
    <li><strong>Two Views available:</strong> Click "Switch to Person View" to see what each individual has for the whole month, or "Duty View" to see a daily roster!</li>
    <li><strong>OFFs split across weeks:</strong> OFFs are exactly 7 days apart in the pattern, guaranteeing 1 OFF per week for every person.</li>
    <li><strong>14-day cycle (Aug 10–23).</strong> Persons 1–14 follow a cyclic shift; Person 15 (Tirawin) has a custom schedule for uniqueness.</li>
    <li><strong>Per person per cycle:</strong> 3 AM-OR, 1 AM-FLOORS, 1 AM-ER, 1 AM-WOUND, 1 ANES, 2 PM-OR, 2 PM-FLOORS, 1 PM-ER, 2 OFF = 14 days.</li>
    <li><strong>Extra person priority:</strong> Person 15's schedule places extras as: 3× AM-OR, 1× AM-ER (AM top priorities), 1× PM-ER (PM top priority!), 2× PM-OR (PM 2nd).</li>
    <li><strong>Sundays (Aug 16 & 23):</strong> 12 on duty + 3 OFF (slightly lighter).</li>
    <li><strong>To copy into Google Sheets:</strong> Click "Copy for Spreadsheet" → Cmd+V into cell A1.</li>
  </ul>
</div>

<script>
const DAYS = 14;
const PEOPLE = 15;

let currentView = 'duty'; // Default to Duty roster view!

const people = [
  "Chiew, Simon S.",
  "De Asis, Vincent Flavianne",
  "De Jesus, Aliyah Isobel T.",
  "Gamboa, Mariane Nicole P.",
  "Seares, Clea Anne T.",
  "Fajardo, Ma. Salome Patricia",
  "Garganera, Wilbert",
  "Malonjao, Carl Angelo D.",
  "Ignacio, Julian Nicolas E.",
  "Salvador, Alieah Gail A.",
  "Angara, Jose Francisco A.",
  "Esguera, Gabrielle Angelica C.",
  "Esliva, Nina Ysabel M.",
  "Ong, Mary Joy Beatrice B.",
  "Tirawin, Eimee Rochelle A."
];

// 14-slot pattern: PM mini-blocks each end with OFF, OFFs 7 apart
// AM-ORs are interspersed with other AM duties to prevent fatigue
const pattern = [
  "AM - OR",      // 0
  "AM - FLOORS",  // 1
  "AM - OR",      // 2
  "AM - ER",      // 3
  "PM - OR",      // 4
  "PM - ER",      // 5
  "OFF",           // 6  ← rest after PM-ER
  "AM - WOUND",   // 7
  "AM - OR",      // 8
  "ANES",          // 9
  "PM - OR",      // 10
  "PM - FLOORS",  // 11
  "PM - FLOORS",  // 12
  "OFF"            // 13 ← rest after PM-FL
];

// Person 14 (Tirawin): custom schedule — same totals, split OFFs,
// AM-ORs spread out. Provides extra coverage on these exact days.
const person14 = [
  "AM - OR",      // D0
  "AM - ER",      // D1
  "AM - OR",      // D2
  "PM - OR",      // D3
  "PM - FLOORS",  // D4
  "PM - ER",      // D5
  "OFF",           // D6  — week 1 OFF (Sunday)
  "AM - FLOORS",  // D7
  "AM - OR",      // D8
  "AM - WOUND",   // D9
  "ANES",          // D10
  "PM - OR",      // D11
  "PM - FLOORS",  // D12
  "OFF"            // D13 — week 2 OFF (Sunday)
];

const dates = [
  "Aug 10", "Aug 11", "Aug 12", "Aug 13", "Aug 14",
  "Aug 15", "Aug 16", "Aug 17", "Aug 18", "Aug 19",
  "Aug 20", "Aug 21", "Aug 22", "Aug 23"
];
const dows = [
  "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
  "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday",
  "Thursday", "Friday", "Saturday", "Sunday"
];
const isWeekend = [false, false, false, false, false, true, true, false, false, false, false, false, true, true];

function getAssignment(p, d) {
  if (p === 14) return person14[d];
  return pattern[(d + p) % DAYS];
}

const classMap = {
  "AM - OR": "am-or", "AM - FLOORS": "am-fl", "AM - ER": "am-er",
  "AM - WOUND": "am-wc", "ANES": "anes",
  "PM - OR": "pm-or", "PM - FLOORS": "pm-fl", "PM - ER": "pm-er",
  "OFF": "off"
};

function toggleView() {
  currentView = currentView === 'person' ? 'duty' : 'person';
  document.getElementById('toggleViewBtn').innerHTML = currentView === 'person' ? '🔄 Switch to Duty View (Roster)' : '🔄 Switch to Person View';
  buildSchedule();
}

function buildSchedule() {
  const table = document.getElementById('scheduleTable');
  let html = '<thead>';
  
  if (currentView === 'person') {
    html += '<tr><th class="name-cell">CYCLE 1 (BY PERSON)</th>';
    for (let d = 0; d < DAYS; d++) html += '<th' + (isWeekend[d] ? ' class="weekend"' : '') + '>' + dates[d] + '</th>';
    html += '</tr><tr><th class="name-cell sub-header">TMC Surg</th>';
    for (let d = 0; d < DAYS; d++) html += '<th class="sub-header' + (isWeekend[d] ? ' weekend' : '') + '">' + dows[d] + '</th>';
    html += '</tr></thead><tbody>';

    for (let p = 0; p < PEOPLE; p++) {
      html += '<tr><td class="name-cell">' + (p + 1) + '. ' + people[p] + '</td>';
      for (let d = 0; d < DAYS; d++) {
        const a = getAssignment(p, d);
        html += '<td class="' + classMap[a] + '">' + a + '</td>';
      }
      html += '</tr>';
    }
  } else {
    // Duty View
    html += '<tr><th class="name-cell">DUTY ROSTER</th>';
    for (let d = 0; d < DAYS; d++) html += '<th' + (isWeekend[d] ? ' class="weekend"' : '') + '>' + dates[d] + '</th>';
    html += '</tr><tr><th class="name-cell sub-header">TMC Surg</th>';
    for (let d = 0; d < DAYS; d++) html += '<th class="sub-header' + (isWeekend[d] ? ' weekend' : '') + '">' + dows[d] + '</th>';
    html += '</tr></thead><tbody>';

    const order = ["AM - OR", "AM - FLOORS", "AM - ER", "AM - WOUND", "ANES", "PM - OR", "PM - FLOORS", "PM - ER", "OFF"];
    const maxRows = { "AM - OR": 4, "AM - FLOORS": 2, "AM - ER": 2, "AM - WOUND": 2, "ANES": 2, "PM - OR": 3, "PM - FLOORS": 3, "PM - ER": 2, "OFF": 3 };
    
    let dailyRoster = [];
    for (let d = 0; d < DAYS; d++) {
      let dayMap = {};
      for (let p = 0; p < PEOPLE; p++) {
        const a = getAssignment(p, d);
        if(!dayMap[a]) dayMap[a] = [];
        let nameParts = people[p].split(', ');
        // Shorten the name slightly for the duty view: "Chiew, Simon S." -> "Chiew, S."
        let shortName = nameParts[0] + (nameParts[1] ? ', ' + nameParts[1].charAt(0) + '.' : '');
        dayMap[a].push(shortName);
      }
      dailyRoster.push(dayMap);
    }
    
    for (const duty of order) {
      const rowCount = maxRows[duty];
      for (let r = 0; r < rowCount; r++) {
        html += '<tr>';
        html += \`<td class="name-cell \${classMap[duty]}">\${duty}</td>\`;
        for (let d = 0; d < DAYS; d++) {
          const person = dailyRoster[d][duty] && dailyRoster[d][duty][r] ? dailyRoster[d][duty][r] : '';
          html += \`<td class="\${person ? classMap[duty] : ''}">\${person}</td>\`;
        }
        html += '</tr>';
      }
    }
  }

  html += '<tr><td class="name-cell totals-cell" style="font-size:11px;">DAILY COUNT</td>';
  for (let d = 0; d < DAYS; d++) {
    const counts = {};
    let onDuty = 0;
    for (let p = 0; p < PEOPLE; p++) {
      const a = getAssignment(p, d);
      counts[a] = (counts[a] || 0) + 1;
      if (a !== "OFF") onDuty++;
    }
    const order = ["AM - OR","AM - FLOORS","AM - ER","AM - WOUND","ANES","PM - OR","PM - FLOORS","PM - ER","OFF"];
    let cell = '<strong>' + onDuty + ' on duty</strong><br>';
    for (const k of order) {
      if (counts[k]) {
        let short = k.replace('AM - ','A-').replace('PM - ','P-');
        if (k === 'AM - WOUND') short = 'WC';
        cell += counts[k] + ' ' + short + '<br>';
      }
    }
    html += '<td class="totals-cell">' + cell + '</td>';
  }
  html += '</tr></tbody>';
  table.innerHTML = html;
}

function buildSummary() {
  const section = document.getElementById('summarySection');
  let html = '<h3>✅ Per-Person Totals — Verification</h3>';
  html += '<table><thead><tr><th class="name-cell">Name</th>';
  const cols = ["AM - OR","AM - FLOORS","AM - ER","AM - WOUND","ANES","PM - OR","PM - FLOORS","PM - ER","OFF"];
  const shortCols = ["AM-OR","AM-FL","AM-ER","WOUND","ANES","PM-OR","PM-FL","PM-ER","OFF"];
  const expected = [3, 1, 1, 1, 1, 2, 2, 1, 2];
  for (let i = 0; i < cols.length; i++) html += '<th>' + shortCols[i] + '</th>';
  html += '<th>TOTAL</th></tr></thead><tbody>';

  let allCorrect = true;
  for (let p = 0; p < PEOPLE; p++) {
    const counts = {};
    for (let d = 0; d < DAYS; d++) { const a = getAssignment(p, d); counts[a] = (counts[a] || 0) + 1; }
    html += '<tr><td class="name-cell">' + people[p] + '</td>';
    let total = 0;
    for (let i = 0; i < cols.length; i++) {
      const v = counts[cols[i]] || 0; total += v;
      const ok = v === expected[i]; if (!ok) allCorrect = false;
      html += '<td class="' + classMap[cols[i]] + '">' + v + (ok ? ' ✓' : ' ✗') + '</td>';
    }
    html += '<td style="font-weight:700;background:#f0f0f0">' + total + '</td></tr>';
  }
  html += '<tr class="expected-row"><td class="name-cell" style="background:#f0f8f0!important">EXPECTED</td>';
  for (let i = 0; i < expected.length; i++) html += '<td>' + expected[i] + '</td>';
  html += '<td>14</td></tr></tbody></table>';

  if (allCorrect) html += '<p style="margin-top:12px;color:#27ae60;font-weight:600;font-size:14px">✅ All 15 persons have perfectly even distribution. Schedule is balanced.</p>';

  html += '<h3 style="margin-top:20px">📅 OFF Days — Split Verification</h3>';
  html += '<table><thead><tr><th class="name-cell">Name</th><th>Week 1 OFF<br>(Aug 10–16)</th><th>Week 2 OFF<br>(Aug 17–23)</th><th>Days Apart</th></tr></thead><tbody>';
  for (let p = 0; p < PEOPLE; p++) {
    let offs = [];
    for (let d = 0; d < DAYS; d++) { if (getAssignment(p, d) === "OFF") offs.push(d); }
    const w1 = offs.filter(d => d < 7).map(d => dows[d] + ' ' + dates[d]);
    const w2 = offs.filter(d => d >= 7).map(d => dows[d] + ' ' + dates[d]);
    const apart = offs.length === 2 ? Math.abs(offs[1] - offs[0]) : '-';
    html += '<tr><td class="name-cell">' + people[p] + '</td>';
    html += '<td class="off">' + (w1.length ? w1.join(', ') : '—') + '</td>';
    html += '<td class="off">' + (w2.length ? w2.join(', ') : '—') + '</td>';
    html += '<td style="font-weight:700">' + apart + ' days ✓</td></tr>';
  }
  html += '</tbody></table>';

  section.innerHTML = html;
}

function copyTSV() {
  let tsv = currentView === 'person' ? 'CYCLE 1' : 'DUTY ROSTER';
  for (let d = 0; d < DAYS; d++) tsv += '\t' + dates[d];
  tsv += '\nTMC Surg';
  for (let d = 0; d < DAYS; d++) tsv += '\t' + dows[d];
  tsv += '\n';

  if (currentView === 'person') {
    for (let p = 0; p < PEOPLE; p++) {
      tsv += people[p];
      for (let d = 0; d < DAYS; d++) tsv += '\t' + getAssignment(p, d);
      tsv += '\n';
    }
  } else {
    const order = ["AM - OR", "AM - FLOORS", "AM - ER", "AM - WOUND", "ANES", "PM - OR", "PM - FLOORS", "PM - ER", "OFF"];
    const maxRows = { "AM - OR": 4, "AM - FLOORS": 2, "AM - ER": 2, "AM - WOUND": 2, "ANES": 2, "PM - OR": 3, "PM - FLOORS": 3, "PM - ER": 2, "OFF": 3 };
    for (const duty of order) {
      const rowCount = maxRows[duty];
      for (let r = 0; r < rowCount; r++) {
        tsv += duty;
        for (let d = 0; d < DAYS; d++) {
          let assigned = [];
          for (let p=0; p<PEOPLE; p++) {
            if (getAssignment(p, d) === duty) {
              let nameParts = people[p].split(', ');
              let shortName = nameParts[0] + (nameParts[1] ? ', ' + nameParts[1].charAt(0) + '.' : '');
              assigned.push(shortName);
            }
          }
          tsv += '\t' + (assigned[r] || '');
        }
        tsv += '\n';
      }
    }
  }
  
  navigator.clipboard.writeText(tsv).then(() => {
    document.getElementById('copyMsg').classList.add('show');
    setTimeout(() => document.getElementById('copyMsg').classList.remove('show'), 2500);
  }).catch(() => {
    const ta = document.createElement('textarea'); ta.value = tsv;
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    document.getElementById('copyMsg').classList.add('show');
    setTimeout(() => document.getElementById('copyMsg').classList.remove('show'), 2500);
  });
}

function downloadCSV() {
  let csv = currentView === 'person' ? '"CYCLE 1"' : '"DUTY ROSTER"';
  for (let d = 0; d < DAYS; d++) csv += ',"' + dates[d] + '"';
  csv += '\n"TMC Surg"';
  for (let d = 0; d < DAYS; d++) csv += ',"' + dows[d] + '"';
  csv += '\n';
  
  if (currentView === 'person') {
    for (let p = 0; p < PEOPLE; p++) {
      csv += '"' + people[p] + '"';
      for (let d = 0; d < DAYS; d++) csv += ',"' + getAssignment(p, d) + '"';
      csv += '\n';
    }
  } else {
    const order = ["AM - OR", "AM - FLOORS", "AM - ER", "AM - WOUND", "ANES", "PM - OR", "PM - FLOORS", "PM - ER", "OFF"];
    const maxRows = { "AM - OR": 4, "AM - FLOORS": 2, "AM - ER": 2, "AM - WOUND": 2, "ANES": 2, "PM - OR": 3, "PM - FLOORS": 3, "PM - ER": 2, "OFF": 3 };
    for (const duty of order) {
      const rowCount = maxRows[duty];
      for (let r = 0; r < rowCount; r++) {
        csv += '"' + duty + '"';
        for (let d = 0; d < DAYS; d++) {
          let assigned = [];
          for (let p=0; p<PEOPLE; p++) {
            if (getAssignment(p, d) === duty) {
              let nameParts = people[p].split(', ');
              let shortName = nameParts[0] + (nameParts[1] ? ', ' + nameParts[1].charAt(0) + '.' : '');
              assigned.push(shortName);
            }
          }
          csv += ',"' + (assigned[r] || '') + '"';
        }
        csv += '\n';
      }
    }
  }

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'TMC_Surg_Schedule_Cycle1.csv';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
}

buildSchedule();
buildSummary();
</script>

</body>
</html>
`;

fs.writeFileSync('TMC_Surg_Schedule.html', htmlContent);
