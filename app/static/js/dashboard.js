/**
 * RoadVision — Dashboard JavaScript
 * ====================================
 * Responsibilities:
 *   - Poll the Flask REST API for updated frames and scene summaries
 *   - Update the dashboard UI with detection results, alerts, and stats
 *   - Handle video file upload and pipeline start/stop controls
 *   - Render object breakdown chart via Chart.js
 *
 * API Endpoints consumed (all served by Flask backend):
 *   POST /api/upload         → upload video file
 *   POST /api/process/start  → start CV pipeline
 *   POST /api/process/stop   → stop CV pipeline
 *   GET  /api/frame          → latest annotated frame (base64 JPEG)
 *   GET  /api/summary        → latest scene summary (JSON)
 *   GET  /api/status         → pipeline running status
 *
 * NOTE: This file is a STUB.
 * Full implementation begins in Phase 2 (Web Application Phase).
 * ====================================
 */

/* ---------------------------------------------------------------------------
   CONFIGURATION
   --------------------------------------------------------------------------- */
const API = {
    upload:       '/api/upload',
    processStart: '/api/process/start',
    processStop:  '/api/process/stop',
    frame:        '/api/frame',
    summary:      '/api/summary',
    status:       '/api/status',
};

const POLL_INTERVAL_MS = 200;   // How often to fetch new frame + summary (ms)

/* ---------------------------------------------------------------------------
   STATE
   --------------------------------------------------------------------------- */
let pollTimer      = null;
let objectChart    = null;
let isRunning      = false;

/* ---------------------------------------------------------------------------
   DOM REFERENCES (populated on DOMContentLoaded)
   --------------------------------------------------------------------------- */
let elVideoFrame, elFrameCounter, elStatusBadge;
let elBtnStart, elBtnStop, elVideoUpload;
let elStatTotal, elStatVehicles, elStatRoadUsers, elStatInfra, elStatHazards;
let elDensityBadge, elStatMoving, elStatStationary;
let elDangerBadge, elAlertsList;

/* ---------------------------------------------------------------------------
   INITIALISATION
   --------------------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    // DOM refs
    elVideoFrame    = document.getElementById('video-frame');
    elFrameCounter  = document.getElementById('frame-counter');
    elStatusBadge   = document.getElementById('status-badge');
    elBtnStart      = document.getElementById('btn-start');
    elBtnStop       = document.getElementById('btn-stop');
    elVideoUpload   = document.getElementById('video-upload');
    elStatTotal         = document.getElementById('stat-total');
    elStatVehicles      = document.getElementById('stat-vehicles');
    elStatRoadUsers     = document.getElementById('stat-road-users');
    elStatInfra         = document.getElementById('stat-infrastructure');
    elStatHazards       = document.getElementById('stat-hazards');
    elDensityBadge      = document.getElementById('density-badge');
    elStatMoving        = document.getElementById('stat-moving');
    elStatStationary    = document.getElementById('stat-stationary');
    elDangerBadge       = document.getElementById('danger-badge');
    elAlertsList        = document.getElementById('alerts-list');

    // Event listeners
    elVideoUpload.addEventListener('change', onVideoSelected);
    elBtnStart.addEventListener('click', onStartClicked);
    elBtnStop.addEventListener('click', onStopClicked);

    // Initialise chart placeholder
    initChart();
});

/* ---------------------------------------------------------------------------
   EVENT HANDLERS
   (Stubs — full implementation in Phase 2)
   --------------------------------------------------------------------------- */

async function onVideoSelected(event) {
    // TODO Phase 2: Upload selected video file to POST /api/upload
    console.log('[RoadVision] Video selected:', event.target.files[0]?.name);
    elBtnStart.disabled = false;
    setStatus('VIDEO LOADED', 'secondary');
}

async function onStartClicked() {
    // TODO Phase 2: POST /api/process/start → start polling
    console.log('[RoadVision] Start clicked');
    isRunning = true;
    elBtnStart.disabled = true;
    elBtnStop.disabled = false;
    setStatus('RUNNING', 'success');
    startPolling();
}

async function onStopClicked() {
    // TODO Phase 2: POST /api/process/stop → stop polling
    console.log('[RoadVision] Stop clicked');
    isRunning = false;
    elBtnStart.disabled = false;
    elBtnStop.disabled = true;
    setStatus('STOPPED', 'danger');
    stopPolling();
}

/* ---------------------------------------------------------------------------
   POLLING LOOP
   (Stubs — full implementation in Phase 2)
   --------------------------------------------------------------------------- */

function startPolling() {
    pollTimer = setInterval(async () => {
        await fetchFrame();
        await fetchSummary();
    }, POLL_INTERVAL_MS);
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
    }
}

async function fetchFrame() {
    // TODO Phase 2: GET /api/frame → update <img> src with base64 JPEG
    // const response = await fetch(API.frame);
    // const data = await response.json();
    // elVideoFrame.src = 'data:image/jpeg;base64,' + data.frame;
    // elFrameCounter.textContent = 'Frame: ' + data.frame_index;
}

async function fetchSummary() {
    // TODO Phase 2: GET /api/summary → update all sidebar stats
    // const response = await fetch(API.summary);
    // const summary = await response.json();
    // updateSummaryUI(summary);
}

/* ---------------------------------------------------------------------------
   UI UPDATE FUNCTIONS
   (Stubs — full implementation in Phase 2)
   --------------------------------------------------------------------------- */

function updateSummaryUI(summary) {
    // TODO Phase 2: Populate all sidebar elements from summary JSON
    elStatTotal.textContent         = summary.total_objects ?? '—';
    elStatVehicles.textContent      = summary.vehicles ?? '—';
    elStatRoadUsers.textContent     = summary.road_users ?? '—';
    elStatInfra.textContent         = summary.infrastructure ?? '—';
    elStatHazards.textContent       = summary.road_hazards ?? '—';
    elStatMoving.textContent        = summary.moving ?? '—';
    elStatStationary.textContent    = summary.stationary ?? '—';

    setDensityBadge(summary.density);
    setDangerBadge(summary.danger_zone_active);
    setAlerts(summary.alerts ?? []);
    updateChart(summary.per_class ?? {});
}

function setDensityBadge(level) {
    elDensityBadge.textContent = level ?? '—';
    elDensityBadge.className = `badge density-badge density-${level}`;
}

function setDangerBadge(active) {
    elDangerBadge.textContent = active ? 'ACTIVE' : 'CLEAR';
    elDangerBadge.className   = `badge danger-badge danger-${active ? 'ACTIVE' : 'CLEAR'}`;
}

function setAlerts(alerts) {
    if (!alerts.length) {
        elAlertsList.innerHTML = '<li class="text-muted small">No alerts</li>';
        return;
    }
    elAlertsList.innerHTML = alerts
        .map(a => `<li>${a}</li>`)
        .join('');
}

function setStatus(label, variant) {
    elStatusBadge.textContent  = label;
    elStatusBadge.className    = `badge bg-${variant} ms-auto`;
}

/* ---------------------------------------------------------------------------
   CHART.JS — Object Breakdown Bar Chart
   (Stub — full implementation in Phase 2)
   --------------------------------------------------------------------------- */

function initChart() {
    const ctx = document.getElementById('object-chart')?.getContext('2d');
    if (!ctx) return;

    objectChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Count',
                data: [],
                backgroundColor: '#f0a500',
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
                y: { ticks: { color: '#8b949e', stepSize: 1 }, grid: { color: '#30363d' }, beginAtZero: true }
            }
        }
    });
}

function updateChart(perClass) {
    if (!objectChart) return;
    const labels = Object.keys(perClass);
    const data   = Object.values(perClass);
    objectChart.data.labels         = labels;
    objectChart.data.datasets[0].data = data;
    objectChart.update();
}
