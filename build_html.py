import json

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Surgery Rotation Schedules</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    /* 
      OFFICIAL GOOGLE SHEETS SCHEDULE PALETTE
      Replicates the exact colors used in the ASMPH / EAMC master spreadsheet.
    */

    /* ER (Emergency) : Google Sheets Red / Peach */
    --tmc-am-er: #fce4d6; --tmc-am-er-text: #c00000;         /* ER Pre: Soft Peach-Red */
    --tmc-pm-er: #c00000; --tmc-pm-er-text: #ffffff;         /* ER Duty: Solid Dark Red */
    --eamc-er: #fce4d6; --eamc-er-text: #c00000;             
    --eamc-er-duty: #c00000; --eamc-er-duty-text: #ffffff;   

    /* OR & Wards Duty : Google Sheets Blue */
    --tmc-am-or: #d9e1f2; --tmc-am-or-text: #1f4e78;         /* Ward/OR Pre: Soft Blue */
    --tmc-pm-or: #2f5597; --tmc-pm-or-text: #ffffff;         /* Ward/OR Duty: Solid Dark Blue */
    --eamc-pre: #d9e1f2; --eamc-pre-text: #1f4e78;           
    --eamc-duty: #2f5597; --eamc-duty-text: #ffffff;         

    /* Floors & Clinics : Google Sheets Green & Yellow */
    --tmc-am-floors: #e2efda; --tmc-am-floors-text: #375623; /* Floors Pre: Soft Mint Green */
    --tmc-pm-floors: #375623; --tmc-pm-floors-text: #ffffff; /* Floors Duty: Solid Dark Green */
    
    /* Specialty & Clinics (EAMC & TMC) */
    --eamc-breast: #e2efda; --eamc-breast-text: #375623;     /* Breast Care: Soft Mint Green */
    --eamc-opd: #fff2cc; --eamc-opd-text: #7f6000;           /* OPD: Soft Yellow */
    --tmc-am-wound: #e4dfec; --tmc-am-wound-text: #3f3151;   /* Wound Care: Soft Lilac */
    --tmc-anes: #ddebf7; --tmc-anes-text: #203764;           /* Anesthesia: Ice Cyan/Blue */

    /* Admin / Off : Google Sheets Grey / White */
    --tmc-off: #ffffff; --tmc-off-text: #595959;
    --eamc-sgd: #ededed; --eamc-sgd-text: #595959;           /* SGD then Off: Soft Grey */
    --eamc-off: #ffffff; --eamc-off-text: #595959;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
    background-color: #f7f9fa;
    color: #37352f;
    padding: 30px 20px;
    min-height: 100vh;
  }
  
  .glass-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border-radius: 8px;
  }

  .header-card {
    padding: 30px; max-width: 900px; margin: 0 auto 30px; text-align: center;
  }
  
  select {
    padding: 8px 14px; font-size: 15px; border-radius: 4px; border: 1px solid #e2e8f0;
    outline: none; background: #ffffff; color: #37352f; font-weight: 500; cursor: pointer; min-width: 300px;
    font-family: inherit;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }
  select:focus, select:hover { border-color: #cbd5e1; background: #f8fafc; transform: none; box-shadow: none; }

  .tabs { display: flex; justify-content: center; gap: 8px; margin-top: 24px; }
  .tab-btn {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #64748b;
    font-weight: 500;
    padding: 8px 16px; font-size: 15px;
    transition: background 0.1s, color 0.1s;
    cursor: pointer; font-family: inherit;
  }
  .tab-btn:hover { background: #f1f5f9; color: #0f172a; transform: none; box-shadow: none !important; }
  .tab-btn.active { 
    background: #f1f5f9; 
    color: #0f172a;
    border: 1px solid #cbd5e1;
    font-weight: 600;
    box-shadow: none !important;
  }

  /* Master Tables */
  .master-view { display: none; margin-bottom: 30px; width: 100%; overflow-x: auto; }
  .master-view.active { display: block; }
  
  table { border-collapse: collapse; font-size: 13px; width: 100%; min-width: 1200px; zoom: 0.7; background: #ffffff; border-radius: 0; overflow: hidden; }
  th, td { border: 1px solid #e2e8f0; padding: 10px 8px; text-align: center; word-wrap: break-word; color: #334155; }
  thead th { 
    background: #f8fafc;
    color: #334155; font-weight: 600; position: sticky; top: 0; z-index: 2; 
    font-size: 12px;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .name-cell { 
    text-align: left !important; font-weight: 600; 
    background: #f8fafc !important;
    width: 220px; position: sticky; left: 0; z-index: 1; 
    padding-left: 16px; white-space: nowrap; 
    border-right: 2px solid #e2e8f0; color: #334155;
  }
  
  tbody tr { transition: background 0.1s; }
  tbody tr:hover td { background: #f1f5f9; }

  /* Calendar View */
  .scroll-wrapper {
    width: 100%; max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;
    margin-bottom: 35px; border-radius: 4px; border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05); background: #ffffff;
  }
  .personal-view { display: none; max-width: 1100px; margin: 0 auto; width: 100%; overflow: hidden; }
  .personal-view.active { display: block; }
  
  .week-grid {
    display: grid; grid-template-columns: 55px repeat(7, 1fr); gap: 0;
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; overflow: hidden; margin-bottom: 35px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  }
  .week-title { grid-column: 1 / -1; background: #f8fafc; color: #0f172a; padding: 12px; font-weight: 600; text-align: left; font-size: 16px; border-bottom: 1px solid #e2e8f0; }
  
  .cal-header { background: #ffffff; text-align: center; padding: 10px; font-weight: 600; font-size: 14px; color: #334155; border-bottom: 1px solid #e2e8f0; border-left: 1px solid #e2e8f0; }
  .time-axis { background: #ffffff; display: flex; flex-direction: column; }
  .time-slot { height: 30px; display: flex; align-items: flex-start; justify-content: flex-end; padding-right: 8px; font-size: 11px; font-weight: 500; color: #64748b; border-bottom: 1px solid #e2e8f0; }
  
  .day-col { background: #ffffff; position: relative; border-left: 1px solid #e2e8f0; }
  /* Hour lines */
  .hour-line { position: absolute; left: 0; right: 0; height: 1px; background: #e2e8f0; }

  /* Event Blocks */
  .event-block {
    position: absolute; left: 2px; right: 2px; border-radius: 3px; padding: 4px 6px;
    font-size: 12px; font-weight: 600; line-height: 1.2; overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 3px solid rgba(0,0,0,0.15);
    display: flex; flex-direction: column; justify-content: flex-start; text-align: left;
    transition: background 0.1s;
  }
  .event-block:hover { z-index: 5; filter: brightness(0.95); transform: none; box-shadow: none; }
  .event-time { font-size: 10px; opacity: 0.8; font-weight: 500; margin-top: 2px; }

  @media (max-width: 800px) { 
    body { padding: 5px 2px; }
    .header-card { padding: 15px 10px; margin-bottom: 15px; }
    h1 { font-size: 20px !important; }
    h2 { font-size: 15px !important; }
    span { font-size: 12px !important; }
    
    select { min-width: 100%; width: 100%; font-size: 12px; padding: 6px; }
    .tabs { flex-direction: column; gap: 4px; margin-top: 15px; }
    .tab-btn { width: 100%; justify-content: center; font-size: 12px; padding: 6px; }
    
    table { zoom: 0.55; }
    
    .scroll-wrapper { border: none; box-shadow: none; margin-bottom: 20px; }
    .week-grid { min-width: 0; width: 100%; grid-template-columns: 30px repeat(7, 1fr); margin-bottom: 15px; }
    .cal-header { font-size: 9px; padding: 4px 1px; }
    .cal-header span { font-size: 8px !important; }
    .time-slot { font-size: 8px; padding-right: 2px; }
    .week-title { font-size: 12px; padding: 6px; }
    
    .event-block { font-size: 8px; padding: 2px; line-height: 1.1; border-left: 2px solid rgba(0,0,0,0.15); border-radius: 2px; }
    .event-time { font-size: 7px; margin-top: 1px; }
  }
</style>
</head>
<body>

<div class="header-card glass-panel">
  <div style="margin-bottom: 25px;">
    <h1 style="margin: 0; text-align: center; line-height: 1.2; font-weight: 700; font-size: 32px; color: #0f172a;">LEC 17-18<br><span style="font-size: 0.6em; opacity: 0.7; font-weight: 500; color: #64748b;">Surgery Rotation Schedule</span></h1>
  </div>
  <select id="namePicker" onchange="renderApp()">
    <option value="ALL">-- Show Full Master Schedules --</option>
    <option value="Angala, Jose Francisco A.">Angala, Jose Francisco A.</option><option value="Chiew, Simon S.">Chiew, Simon S.</option><option value="De Asis, Vincent Flavianne">De Asis, Vincent Flavianne</option><option value="De Jesus, Aliyah Isobel T.">De Jesus, Aliyah Isobel T.</option><option value="Esguera, Gabrielle Angelica G.">Esguera, Gabrielle Angelica G.</option><option value="Estiva, Nina Ysabel M.">Estiva, Nina Ysabel M.</option><option value="Fajardo, Ma. Salome Patricia A.">Fajardo, Ma. Salome Patricia A.</option><option value="Gamboa, Mariane Nicole P.">Gamboa, Mariane Nicole P.</option><option value="Garganera, Wilbert">Garganera, Wilbert</option><option value="Ignacio, Julian Nicolas E.">Ignacio, Julian Nicolas E.</option><option value="Malonjao, Carl Angelo D.">Malonjao, Carl Angelo D.</option><option value="Ong, Mary Joy Beatrice B.">Ong, Mary Joy Beatrice B.</option><option value="Salvador, Alison Gail A.">Salvador, Alison Gail A.</option><option value="Seares, Clea Anne T.">Seares, Clea Anne T.</option><option value="Tinawin, Eimee Rochelle A.">Tinawin, Eimee Rochelle A.</option>
  </select>
  <div class="tabs" id="mainTabs" style="display:none;">
    <button class="tab-btn active" style="display: flex; align-items: center;" onclick="setTab('eamc')"><img src="eamc_logo.png" style="height:20px; width:20px; object-fit:contain; margin-right:8px; mix-blend-mode: multiply;"> EAMC (Jul 27-Aug 9)</button>
    <button class="tab-btn" style="display: flex; align-items: center;" onclick="setTab('tmc')"><img src="tmc_logo.png" style="height:20px; width:20px; object-fit:contain; border-radius:50%; margin-right:8px; mix-blend-mode: multiply;"> TMC Surg (Aug 10-23)</button>
  </div>
</div>

<div id="masterViewWrap">
  <div class="master-view glass-panel active" id="eamcMaster">
    <h2 style="padding:16px;text-align:center;">🏥 EAMC (Jul 27-Aug 9)</h2>
    <h3 style="padding:8px;text-align:center;background:#ecf0f1;">Week 1</h3>
    <table id="eamcTable1"></table>
    <h3 style="padding:8px;text-align:center;background:#ecf0f1;margin-top:20px;">Week 2</h3>
    <table id="eamcTable2"></table>
  </div>
  <div class="master-view glass-panel active" id="tmcMaster">
    <h2 style="padding:16px;text-align:center;">🏥 TMC Surg (Aug 10-23)</h2>
    <h3 style="padding:8px;text-align:center;background:#ecf0f1;">Week 1</h3>
    <table id="tmcTable1"></table>
    <h3 style="padding:8px;text-align:center;background:#ecf0f1;margin-top:20px;">Week 2</h3>
    <table id="tmcTable2"></table>
  </div>
</div>

<div id="personalView" class="personal-view"></div>

<script>
const masterPeople = ["Chiew, Simon S.", "De Asis, Vincent Flavianne", "De Jesus, Aliyah Isobel T.", "Gamboa, Mariane Nicole P.", "Seares, Clea Anne T.", "Fajardo, Ma. Salome Patricia A.", "Garganera, Wilbert", "Malonjao, Carl Angelo D.", "Ignacio, Julian Nicolas E.", "Salvador, Alison Gail A.", "Angala, Jose Francisco A.", "Esguera, Gabrielle Angelica G.", "Estiva, Nina Ysabel M.", "Ong, Mary Joy Beatrice B.", "Tinawin, Eimee Rochelle A."];
const eamcGroupedPeople = ["De Asis, Vincent Flavianne", "Gamboa, Mariane Nicole P.", "De Jesus, Aliyah Isobel T.", "Ong, Mary Joy Beatrice B.", "Estiva, Nina Ysabel M.", "Chiew, Simon S.", "Malonjao, Carl Angelo D.", "Angala, Jose Francisco A.", "Ignacio, Julian Nicolas E.", "Garganera, Wilbert", "Seares, Clea Anne T.", "Salvador, Alison Gail A.", "Tinawin, Eimee Rochelle A.", "Fajardo, Ma. Salome Patricia A.", "Esguera, Gabrielle Angelica G."];
const tmcGrid = [["PM - OR", "OFF", "AM - OR", "ANES", "AM - FLOORS", "OFF", "AM - ER", "PM - ER", "OFF", "AM - OR", "AM - OR", "PM - FLOORS", "PM - OR", "PM - FLOORS"], ["AM - ER", "PM - ER", "PM - FLOORS", "OFF", "AM - WOUND", "AM - OR", "PM - FLOORS", "OFF", "AM - OR", "AM - FLOORS", "PM - OR", "PM - OR", "OFF", "AM - OR"], ["AM - WOUND", "AM - OR", "ANES", "AM - OR", "OFF", "AM - ER", "AM - OR", "OFF", "AM - FLOORS", "PM - FLOORS", "PM - OR", "PM - FLOORS", "OFF", "PM - OR"], ["PM - OR", "PM - FLOORS", "OFF", "AM - OR", "AM - OR", "AM - FLOORS", "OFF", "AM - OR", "AM - WOUND", "AM - ER", "ANES", "PM - ER", "PM - FLOORS", "PM - OR"], ["ANES", "AM - WOUND", "AM - OR", "PM - FLOORS", "PM - OR", "PM - ER", "OFF", "AM - ER", "PM - OR", "OFF", "AM - ER", "AM - OR", "AM - OR", "OFF"], ["OFF", "PM - FLOORS", "PM - OR", "PM - ER", "PM - FLOORS", "PM - OR", "OFF", "ANES", "AM - ER", "AM - OR", "AM - OR", "AM - OR", "OFF", "AM - FLOORS"], ["AM - OR", "AM - ER", "PM - ER", "OFF", "AM - OR", "AM - WOUND", "AM - OR", "AM - FLOORS", "ANES", "OFF", "PM - FLOORS", "PM - OR", "PM - FLOORS", "OFF"], ["PM - FLOORS", "PM - OR", "OFF", "AM - FLOORS", "PM - ER", "PM - FLOORS", "PM - OR", "OFF", "AM - OR", "ANES", "AM - OR", "AM - WOUND", "AM - ER", "OFF"], ["PM - FLOORS", "PM - OR", "PM - FLOORS", "PM - OR", "OFF", "AM - OR", "ANES", "AM - WOUND", "AM - OR", "AM - OR", "PM - ER", "OFF", "AM - FLOORS", "AM - ER"], ["AM - OR", "AM - OR", "AM - FLOORS", "AM - ER", "AM - OR", "PM - FLOORS", "PM - OR", "PM - OR", "PM - FLOORS", "OFF", "AM - WOUND", "ANES", "PM - ER", "OFF"], ["AM - OR", "AM - FLOORS", "OFF", "AM - OR", "ANES", "OFF", "PM - FLOORS", "PM - FLOORS", "PM - ER", "PM - OR", "OFF", "AM - ER", "AM - WOUND", "AM - OR"], ["AM - FLOORS", "AM - OR", "AM - WOUND", "PM - FLOORS", "OFF", "AM - OR", "PM - ER", "PM - OR", "OFF", "PM - OR", "PM - FLOORS", "OFF", "ANES", "AM - ER"], ["OFF", "AM - OR", "PM - OR", "OFF", "AM - ER", "ANES", "AM - FLOORS", "PM - FLOORS", "PM - OR", "PM - ER", "OFF", "AM - OR", "AM - OR", "PM - FLOORS"], ["OFF", "ANES", "AM - OR", "PM - OR", "PM - FLOORS", "OFF", "AM - ER", "AM - OR", "AM - OR", "AM - WOUND", "AM - FLOORS", "OFF", "PM - OR", "PM - ER"], ["PM - ER", "OFF", "AM - ER", "AM - WOUND", "PM - OR", "PM - OR", "OFF", "AM - OR", "PM - FLOORS", "PM - FLOORS", "OFF", "AM - FLOORS", "AM - OR", "ANES"]];
const eamcSchedule = {"De Asis, Vincent Flavianne": ["Ward/OR Pre - GS1", "ER Pre", "ER Duty", "SGD then Off", "ER Pre", "Ward/OR Duty - GS2", "SGD then Off", "Breast Care", "Ward/OR Duty - GS2", "SGD then Off", "Ward/OR Pre - GS3", "ER Duty", "Off", "Ward/OR Pre - GS3"], "Gamboa, Mariane Nicole P.": ["ER Pre", "ER Duty", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "SGD then Off", "Breast Care*", "Ward/OR Pre - GS2", "Ward/OR Duty - GS2", "Off", "OPD", "Ward/OR Duty - GS3", "Off", "ER Pre"], "De Jesus, Aliyah Isobel T.": ["SGD then Off", "Ward/OR Pre - GS1", "Breast Care", "ER Duty", "SGD then Off", "ER Pre", "OPD*", "ER Pre", "Ward/OR Pre - GS2", "ER Duty", "Off", "Ward/OR Pre - GS3", "Ward/OR Duty - GS3", "SGD then Off"], "Ong, Mary Joy Beatrice B.": ["Ward/OR Duty - GS1", "SGD then Off", "ER Pre", "Breast Care", "Ward/OR Pre - GS1", "OPD*", "Ward/OR Pre - GS2", "ER Duty", "Off", "ER Pre", "ER Duty", "SGD then Off", "Ward/OR Pre - GS3", "Ward/OR Duty - GS3"], "Estiva, Nina Ysabel M.": ["Ward/OR Duty - GS1", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "Off", "Ward/OR Pre - GS2", "Ward/OR Duty - GS2", "SGD then Off", "ER Pre", "Ward/OR Pre - GS2", "ER Pre", "ER Duty", "SGD then Off", "OPD*"], "Chiew, Simon S.": ["Breast Care", "ER Pre", "Ward/OR Duty - GS3", "SGD then Off", "Ward/OR Pre - GS3", "Ward/OR Duty - GS1", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "SGD then Off", "Ward/OR Pre - GS2", "OPD", "ER Duty", "Off"], "Malonjao, Carl Angelo D.": ["ER Pre", "OPD", "Ward/OR Duty - GS3", "Off", "Breast Care", "Ward/OR Pre - GS1", "Ward/OR Duty - GS1", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "SGD then Off", "Ward/OR Pre - GS2", "ER Pre", "ER Duty - until 1 AM"], "Angala, Jose Francisco A.": ["Off", "Ward/OR Pre - GS3", "OPD", "ER Pre", "Ward/OR Duty - GS3", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "SGD then Off", "ER Pre", "Breast Care", "Ward/OR Duty - GS2", "SGD then Off", "Ward/OR Pre - GS2"], "Ignacio, Julian Nicolas E.": ["OPD", "Breast Care", "Ward/OR Pre - GS3", "ER Pre", "ER Duty", "SGD then Off", "ER Pre", "Ward/OR Duty - GS1", "SGD then Off", "Ward/OR Pre - GS1", "ER Duty", "Off", "Ward/OR Pre - GS2", "Ward/OR Duty - GS2"], "Garganera, Wilbert": ["Ward/OR Pre - GS3", "ER Duty", "SGD then Off", "Ward/OR Pre - GS3", "Ward/OR Duty - GS3", "Off", "ER Pre", "Ward/OR Duty - GS1", "SGD then Off", "OPD", "ER Pre", "Breast Care", "ER Duty", "SGD then Off"], "Seares, Clea Anne T.": ["Off", "Ward/OR Pre - GS2", "ER Duty", "SGD then Off", "ER Pre", "Ward/OR Pre - GS3", "ER Duty", "SGD then Off", "OPD", "Ward/OR Duty - GS3", "SGD then Off", "Ward/OR Pre - GS1", "ER Pre", "Breast Care*"], "Salvador, Alison Gail A.": ["SGD then Off", "Ward/OR Duty - GS2", "Off", "OPD", "Ward/OR Pre - GS2", "ER Duty", "SGD then Off", "ER Pre", "Breast Care", "Ward/OR Pre - GS3", "Ward/OR Duty - GS1", "SGD then Off", "Ward/OR Pre - GS1", "ER Pre"], "Tinawin, Eimee Rochelle A.": ["ER Duty", "Off", "ER Pre", "Ward/OR Duty - GS2", "SGD then Off", "Breast Care*", "Ward/OR Pre - GS3", "OPD", "ER Duty", "SGD then Off", "Ward/OR Pre - GS1", "ER Pre", "Ward/OR Duty - GS1", "SGD then Off"], "Fajardo, Ma. Salome Patricia A.": ["Ward/OR Pre - GS2", "Ward/OR Duty - GS2", "SGD then Off", "Ward/OR Pre - GS2", "OPD", "ER Duty", "Off", "Ward/OR Pre - GS3", "ER Pre", "Ward/OR Duty - GS3", "SGD then Off", "ER Pre", "Breast Care*", "ER Duty - until 1 AM"], "Esguera, Gabrielle Angelica G.": ["ER Duty", "SGD then Off", "Ward/OR Pre - GS2", "Ward/OR Duty - GS2", "SGD then Off", "ER Pre", "ER Duty", "Off", "Ward/OR Pre - GS3", "Breast Care", "Ward/OR Duty - GS1", "SGD then Off", "OPD*", "Ward/OR Pre - GS1"]};

const eamcDates = ["Jul 27","Jul 28","Jul 29","Jul 30","Jul 31","Aug 1","Aug 2","Aug 3","Aug 4","Aug 5","Aug 6","Aug 7","Aug 8","Aug 9"];
const tmcDates = ["Aug 10","Aug 11","Aug 12","Aug 13","Aug 14","Aug 15","Aug 16","Aug 17","Aug 18","Aug 19","Aug 20","Aug 21","Aug 22","Aug 23"];
const dows = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun","Mon","Tue","Wed","Thu","Fri","Sat","Sun"];

let currentTab = 'eamc';

function getTmcStyle(shift) {
  if (shift === "AM - OR") return "background:#d9e1f2; color:#1f4e78; border-color:#1f4e78;";
  if (shift === "PM - OR") return "background:#2f5597; color:#ffffff; border-color:#1f4e78;";
  if (shift === "AM - FLOORS") return "background:#e2efda; color:#375623; border-color:#375623;";
  if (shift === "PM - FLOORS") return "background:#375623; color:#ffffff; border-color:#375623;";
  if (shift === "AM - ER") return "background:#fce4d6; color:#c00000; border-color:#c00000;";
  if (shift === "PM - ER") return "background:#c00000; color:#ffffff; border-color:#c00000;";
  if (shift === "AM - WOUND") return "background:#fce7f3; color:#be185d; border-color:#be185d;";
  if (shift === "ANES") return "background:#f3e8ff; color:#7e22ce; border-color:#7e22ce;";
  return "background:#f8fafc; color:#475569; font-weight:800; border-color:#cbd5e1;";
}

function getEamcStyle(shift) {
  if (shift.includes("Ward/OR Pre")) return "background:#d9e1f2; color:#1f4e78; border-color:#1f4e78;";
  if (shift.includes("Ward/OR Duty")) return "background:#2f5597; color:#ffffff; border-color:#1f4e78;";
  if (shift.includes("ER Pre")) return "background:#fce4d6; color:#c00000; border-color:#c00000;";
  if (shift.includes("ER Duty")) return "background:#c00000; color:#ffffff; border-color:#c00000;";
  if (shift.includes("Breast Care")) return "background:#e2efda; color:#375623; border-color:#375623;";
  if (shift.includes("OPD")) return "background:#fff2cc; color:#7f6000; border-color:#7f6000;";
  if (shift === "SGD then Off") return "background:#e4dfec; color:#3f3151; border-color:#3f3151;";
  return "background:#f8fafc; color:#475569; font-weight:800; border-color:#cbd5e1;";
}

function formatTime(s, e) {
  let sh = s % 24; let eh = e % 24;
  let sp = sh>=12 ? (sh===12?12:sh-12)+'pm' : (sh===0?12:sh)+'am';
  let ep = eh>=12 ? (eh===12?12:eh-12)+'pm' : (eh===0?12:eh)+'am';
  return sp + " - " + ep;
}

// Flat array of absolute hour intervals
function buildPersonal(name) {
  const tmcIndex = masterPeople.indexOf(name);
  let html = `<div style="text-align:center;margin-bottom:20px;">
                <h2>Schedule for: <span style="color:#2980b9">${name}</span></h2>
                <button class="tab-btn active" style="margin-top:10px; padding: 10px 20px; font-size: 14px; border-radius: 8px; cursor: pointer; border: none; background: #2980b9; color: white;" onclick="downloadICS('${name}')">
                  📅 Export to Apple / Google Calendar (.ics)
                </button>
                <div style="font-size:11px; color:#777; margin-top:8px;">
                  <strong>Apple Calendar:</strong> Just tap the downloaded file on your iPhone/Mac.<br>
                  <strong>Google Calendar:</strong> Download the file, go to calendar.google.com -> Settings -> Import & Export
                </div>
              </div>`;
  
  let eamcEvents = getAbsoluteEvents(eamcSchedule[name], parseEamcLogic);
  let tmcEvents = getAbsoluteEvents(tmcGrid[tmcIndex], parseTmcLogic);

  const sgdStyle = "background: #1e293b; color: #ffffff; border-left: 3px solid #0f172a; box-shadow: rgba(0, 0, 0, 0.2) 0px 4px 12px; z-index: 10;";
  eamcEvents.push({ title: "[SGD] Dr. Doble", s: 0 * 24 + 13, e: 0 * 24 + 15, c: sgdStyle });
  eamcEvents.push({ title: "[SGD] Dr. Cabrera", s: 3 * 24 + 11, e: 3 * 24 + 13, c: sgdStyle });
  eamcEvents.push({ title: "[SGD] Dr. Chuasuan", s: 4 * 24 + 9, e: 4 * 24 + 11, c: sgdStyle });
  eamcEvents.push({ title: "[SGD] Dr. Ordoñez (Intraop) TBA", s: 4 * 24 + 11, e: 4 * 24 + 13, c: sgdStyle });
  eamcEvents.push({ title: "[SGD] Dr. Chuasuan", s: 8 * 24 + 9, e: 8 * 24 + 11, c: sgdStyle });
  eamcEvents.push({ title: "[SGD] Dr. Amponin", s: 11 * 24 + 9, e: 11 * 24 + 11, c: sgdStyle });

  html += `
  <div style="margin: 40px 0 20px; display: flex; align-items: center; gap: 12px; background: #ffffff; padding: 12px 20px; border-radius: 4px; border: 1px solid #e2e8f0; box-shadow: rgba(0, 0, 0, 0.05) 0px 4px 6px; text-align: left;">
    <img src="eamc_logo.png" style="height: 40px; width: 40px; object-fit: contain; mix-blend-mode: multiply;">
    <div>
      <h2 style="margin: 0; color: #0f172a; font-size: 20px; font-weight: 600;">East Avenue Medical Center (EAMC)</h2>
      <span style="font-size: 14px; font-weight: 500; color: #64748b;">July 27 - Aug 9</span>
    </div>
  </div>`;
  html += renderWeek("Week 1", eamcDates.slice(0,7), dows.slice(0,7), eamcEvents, 0);
  html += renderWeek("Week 2", eamcDates.slice(7,14), dows.slice(7,14), eamcEvents, 7);

  html += `
  <div style="margin: 50px 0 20px; display: flex; align-items: center; gap: 12px; background: #ffffff; padding: 12px 20px; border-radius: 4px; border: 1px solid #e2e8f0; box-shadow: rgba(0, 0, 0, 0.05) 0px 4px 6px; text-align: left;">
    <img src="tmc_logo.png" style="height: 40px; width: 40px; object-fit: contain; border-radius: 50%; mix-blend-mode: multiply;">
    <div>
      <h2 style="margin: 0; color: #0f172a; font-size: 20px; font-weight: 600;">The Medical City (TMC)</h2>
      <span style="font-size: 14px; font-weight: 500; color: #64748b;">Aug 10 - Aug 23</span>
    </div>
  </div>`;
  html += renderWeek("Week 1", tmcDates.slice(0,7), dows.slice(0,7), tmcEvents, 0);
  html += renderWeek("Week 2", tmcDates.slice(7,14), dows.slice(7,14), tmcEvents, 7);
  
  document.getElementById("personalView").innerHTML = html;
}

function downloadICS(name) {
  const tmcIndex = masterPeople.indexOf(name);
  let eamcEvts = getAbsoluteEvents(eamcSchedule[name], parseEamcLogic);
  let tmcEvts = getAbsoluteEvents(tmcGrid[tmcIndex], parseTmcLogic);
  
  let ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Surgery Rotation//EN\n";
  
  function addEvents(evts, baseDateStr, prefix) {
    let baseDate = new Date(baseDateStr);
    for (let e of evts) {
      if (e.title.includes("OFF") || e.title === "OFF" || e.title.includes("TRUE FROM")) continue; 
      
      let start = new Date(baseDate.getTime() + e.s * 3600000);
      let end = new Date(baseDate.getTime() + e.e * 3600000);
      
      let format = (d) => {
        let y = d.getFullYear();
        let m = String(d.getMonth()+1).padStart(2,'0');
        let day = String(d.getDate()).padStart(2,'0');
        let h = String(d.getHours()).padStart(2,'0');
        let min = String(d.getMinutes()).padStart(2,'0');
        let s = String(d.getSeconds()).padStart(2,'0');
        return `${y}${m}${day}T${h}${min}${s}`;
      };
      
      ics += "BEGIN:VEVENT\n";
      ics += `UID:${Math.random().toString(36).substring(2)}@surgery\n`;
      ics += `DTSTAMP:${format(new Date())}\n`;
      ics += `DTSTART:${format(start)}\n`;
      ics += `DTEND:${format(end)}\n`;
      ics += `SUMMARY:${prefix} ${e.title}\n`;
      ics += "END:VEVENT\n";
    }
  }
  
  addEvents(eamcEvts, "2026-07-27T00:00:00", "[EAMC]");
  addEvents(tmcEvts, "2026-08-10T00:00:00", "[TMC]");
  
  ics += "END:VCALENDAR";
  
  let blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
  let link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${name.replace(/\s+/g, '_')}_Surgery_Schedule.ics`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function getAbsoluteEvents(schedArr, parseLogic) {
  let allEvents = [];
  for(let d=0; d<14; d++) {
    let dayEvents = parseLogic(schedArr[d], dows[d], d);
    allEvents.push(...dayEvents);
  }
  return allEvents;
}

function parseEamcLogic(shift, dow, dayIndex) {
  let evts = [];
  let baseHour = dayIndex * 24;
  let s, e;
  
  if (shift.includes("Breast Care")) {
    if (dow === "Sat" || dow === "Sun") {
      s = baseHour + 7; e = baseHour + 19;
      if (dow === "Sat") e = baseHour + 13;
      evts.push({ title: "ER (from Breast Care)", s, e, c: getEamcStyle("ER Pre") });
    } else {
      evts.push({ title: shift, s: baseHour + 7, e: baseHour + 17, c: getEamcStyle("Breast Care") });
    }
  } else if (shift.includes("OPD")) {
    if (dow === "Sat") {
      evts.push({ title: "OPD", s: baseHour + 7, e: baseHour + 12, c: getEamcStyle("OPD") });
      evts.push({ title: "WARD/OR", s: baseHour + 12, e: baseHour + 13, c: getEamcStyle("Ward/OR Pre") });
    } else if (dow === "Sun") {
      evts.push({ title: "WARD/OR", s: baseHour + 7, e: baseHour + 19, c: getEamcStyle("Ward/OR Pre") });
    } else {
      evts.push({ title: shift, s: baseHour + 7, e: baseHour + 17, c: getEamcStyle("OPD") });
    }
  } else if (shift === "SGD then Off") {
    evts.push({ title: "SGD/Conference", s: baseHour + 7, e: baseHour + 12, c: getEamcStyle(shift) });
  } else if (shift === "Off") {
    s = baseHour + 7; e = baseHour + 17;
    if (dow === "Sat") e = baseHour + 13;
    evts.push({ title: "TRUE FROM (OFF)", s, e, c: "background:#fff; color:#555; border-color:#bdc3c7;" });
  } else if (shift.includes("Duty") || shift.includes("- until 1 AM")) {
    s = baseHour + 19; e = baseHour + 31;
    if (dow === "Wed") s = baseHour + 21;
    evts.push({ title: shift, s, e, c: getEamcStyle(shift) });
  } else {
    s = baseHour + 7; e = baseHour + 19;
    if (dow === "Wed") e = baseHour + 17;
    if (dow === "Sat") e = baseHour + 13;
    evts.push({ title: shift, s, e, c: getEamcStyle(shift) });
  }
  
  if (dow === "Wed") {
    evts.push({ title: "MBA Class", s: baseHour + 18, e: baseHour + 20, c: "background:#8e44ad; color:#fff; border-color:#732d91;" });
  }
  if (dow === "Sat") {
    evts.push({ title: "MBA Class", s: baseHour + 14, e: baseHour + 18, c: "background:#8e44ad; color:#fff; border-color:#732d91;" });
  }
  
  return evts;
}

function parseTmcLogic(shift, dow, dayIndex) {
  let evts = [];
  let baseHour = dayIndex * 24;
  let s, e;
  let isNoClassWed = (dow === "Wed" && dayIndex === 9);
  
  if (shift.startsWith("AM") || shift === "ANES") {
    s = baseHour + 6; e = baseHour + 18;
    evts.push({ title: shift, s, e, c: getTmcStyle(shift) });
  } else if (shift.startsWith("PM")) {
    s = baseHour + 18; e = baseHour + 30;
    if (dow === "Wed" && !isNoClassWed) s = baseHour + 20; // after MBA class
    evts.push({ title: shift, s, e, c: getTmcStyle(shift) });
  } else {
    s = baseHour + 6; e = baseHour + 18;
    evts.push({ title: "OFF (5:30 am relieved)", s, e, c: "background:#f8fafc; color:#475569; border-color:#cbd5e1;" });
  }
  
  if (dow === "Tue") {
    let confText = "Conference (via Zoom)";
    if (shift === "PM - FLOORS") confText = "Conference (Face to Face)";
    evts.push({ title: confText, s: baseHour + 18, e: baseHour + 20, c: "background:#eab308; color:#fff; border-color:#ca8a04; z-index:15;" });
  }
  
  if (dow === "Wed" && !isNoClassWed) {
    evts.push({ title: "MBA Class", s: baseHour + 18, e: baseHour + 20, c: "background:#8e44ad; color:#fff; border-color:#732d91; z-index:15;" });
  }
  if (dow === "Sat") {
    evts.push({ title: "MBA Class", s: baseHour + 14, e: baseHour + 18, c: "background:#8e44ad; color:#fff; border-color:#732d91; z-index:15;" });
  }
  
  return evts;
}

function renderWeek(title, dates, dowArr, allEvents, weekStartIndex) {
  let html = `<div class="scroll-wrapper">`;
  html += `<div class="week-grid" style="margin-bottom: 0; box-shadow: none; border: none; border-radius: 0;">`;
  html += `<div class="week-title">${title}</div><div class="time-axis"><div class="cal-header">Time</div>`;
  for(let i=0;i<24;i++) {
    let ampm = i>=12 ? (i===12?12:i-12)+' PM' : (i===0?12:i)+' AM';
    html += `<div class="time-slot">${ampm}</div>`;
  }
  html += `</div>`;
  
  for(let d=0;d<7;d++) {
    let globalDayIndex = weekStartIndex + d;
    let dayStartHour = globalDayIndex * 24;
    let dayEndHour = dayStartHour + 24;

    html += `<div class="day-col" data-date="${dates[d]}"><div class="cal-header" style="position: sticky; top: 0; z-index: 10;">${dowArr[d]}<br><span style="font-size:10px;font-weight:400">${dates[d]}</span></div>`;
    html += `<div class="timeline-container" style="height:720px; position:relative;">`;
    for(let i=0;i<=24;i++) html += `<div class="hour-line" style="top:${(i/24)*100}%;"></div>`;
    
    // Filter events overlapping this specific 12AM-12AM day window
    for(let e of allEvents) {
      let overlapStart = Math.max(e.s, dayStartHour);
      let overlapEnd = Math.min(e.e, dayEndHour);
      
      if(overlapStart < overlapEnd) {
        let top = ((overlapStart - dayStartHour) / 24) * 100;
        let height = ((overlapEnd - overlapStart) / 24) * 100;
        html += `<div class="event-block" style="top:${top}%; height:${height}%; ${e.c}">
                   ${e.title}<div class="event-time">${formatTime(overlapStart, overlapEnd)}</div>
                 </div>`;
      }
    }
    html += `</div></div>`;
  }
  html += `</div></div>`;
  return html;
}

function renderApp() {
  const sel = document.getElementById("namePicker").value;
  if (sel === "ALL") {
  document.getElementById("personalView").classList.remove("active");
    document.getElementById("masterViewWrap").style.display = "block";
    document.getElementById("mainTabs").style.display = "flex";
    buildMasters();
    setTab(currentTab);
  } else {
    document.getElementById("masterViewWrap").style.display = "none";
    document.getElementById("mainTabs").style.display = "none";
    document.getElementById("personalView").classList.add("active");
    buildPersonal(sel);
  }
  updateCurrentTimeLine();
}

function updateCurrentTimeLine() {
  const now = new Date();
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const dateStr = monthNames[now.getMonth()] + " " + now.getDate();
  const hour = now.getHours() + now.getMinutes() / 60;
  
  document.querySelectorAll('.current-time-line').forEach(el => el.remove());
  
  const cols = document.querySelectorAll(`.day-col[data-date="${dateStr}"] > .timeline-container`);
  cols.forEach(col => {
    const topPct = (hour / 24) * 100;
    const line = document.createElement('div');
    line.className = 'current-time-line';
    line.style.cssText = `position: absolute; left: 0; right: 0; top: ${topPct}%; height: 2px; background: #ff3b30; z-index: 10; pointer-events: none;`;
    
    const dot = document.createElement('div');
    dot.style.cssText = `position: absolute; left: -4px; top: -4px; width: 10px; height: 10px; background: #ff3b30; border-radius: 50%;`;
    line.appendChild(dot);
    
    col.appendChild(line);
  });
}
setInterval(updateCurrentTimeLine, 60000);

function setTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.remove('active');
    if (b.getAttribute('onclick').includes(tab)) b.classList.add('active');
  });
  document.getElementById("eamcMaster").style.display = tab==='eamc'?'block':'none';
  document.getElementById("tmcMaster").style.display = tab==='tmc'?'block':'none';
}

function buildMasterTable(title, dates, dowArr, schedule, peopleList, getStyleFn, weekOffset) {
  let h = `<thead><tr><th class="name-cell">${title}</th>`;
  for(let i=0;i<7;i++) h+=`<th>${dates[weekOffset+i]}<br>${dowArr[weekOffset+i]}</th>`;
  h+='</tr></thead><tbody>';
  for(let p=0;p<15;p++) {
    const name = peopleList[p];
    h+=`<tr class="${p%5===4?'group-end':''}"><td class="name-cell">${p+1}. ${name}</td>`;
    for(let d=0;d<7;d++) {
      let shift = schedule[name] ? schedule[name][weekOffset+d] : schedule[p][weekOffset+d];
      h+=`<td style="${getStyleFn(shift)}">${shift}</td>`;
    }
    h+='</tr>';
  }
  h+='</tbody>';
  return h;
}

function buildMasters() {
  document.getElementById("eamcTable1").innerHTML = buildMasterTable("EAMC", eamcDates, dows, eamcSchedule, eamcGroupedPeople, getEamcStyle, 0);
  document.getElementById("eamcTable2").innerHTML = buildMasterTable("EAMC", eamcDates, dows, eamcSchedule, eamcGroupedPeople, getEamcStyle, 7);
  document.getElementById("tmcTable1").innerHTML = buildMasterTable("TMC", tmcDates, dows, tmcGrid, masterPeople, getTmcStyle, 0);
  document.getElementById("tmcTable2").innerHTML = buildMasterTable("TMC", tmcDates, dows, tmcGrid, masterPeople, getTmcStyle, 7);
}

renderApp();
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
