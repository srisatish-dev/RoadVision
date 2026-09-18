/**
 * RoadVision — AI Vision Intelligence Dashboard JavaScript
 * ============================================================
 * Handles video file processing & live webcam real-time analysis,
 * MJPEG frame streaming, unique physical object tracking statistics,
 * modern glassmorphism UI updates, and Chart.js integration.
 */

let objectChart = null;
let uploadedFilename = null;
let webcamPollTimer = null;

// Category mappings matching config
const CATEGORIES = {
    vehicles: ['car', 'bus', 'truck', 'motorcycle', 'bicycle', 'auto-rickshaw'],
    road_users: ['person'],
    infrastructure: ['traffic light', 'stop sign', 'road barrier'],
    road_hazards: ['pothole', 'construction debris']
};

document.addEventListener('DOMContentLoaded', () => {
    // Mode Radios
    const modeFile   = document.getElementById('mode-file');
    const modeWebcam = document.getElementById('mode-webcam');
    const fileControls   = document.getElementById('file-controls');
    const webcamControls = document.getElementById('webcam-controls');

    // DOM Elements - Video File Mode
    const elVideoUpload    = document.getElementById('video-upload');
    const elFileName       = document.getElementById('selected-file-name');
    const elBtnStart       = document.getElementById('btn-start');
    const elBtnDownload    = document.getElementById('btn-download');

    // DOM Elements - Live Camera Mode
    const elBtnWebcamStart = document.getElementById('btn-webcam-start');
    const elBtnWebcamStop  = document.getElementById('btn-webcam-stop');

    // Common DOM Elements
    const elProcessStatus    = document.getElementById('process-status');
    const elStatusBadge      = document.getElementById('status-badge');
    const elStatusPulse      = document.getElementById('status-pulse');
    const elLoadingOverlay   = document.getElementById('loading-overlay');
    const elVideoStream      = document.getElementById('video-stream');
    const elVideoPlaceholder = document.getElementById('video-placeholder');
    const elOverlayBadges    = document.getElementById('video-overlay-badges');

    // -----------------------------------------------------------------------
    // MODE SWITCHING
    // -----------------------------------------------------------------------
    modeFile.addEventListener('change', () => {
        if (modeFile.checked) {
            fileControls.classList.remove('d-none');
            webcamControls.classList.add('d-none');
            stopWebcamStream();
            resetDisplay();
            setSystemStatus('SYSTEM READY', 'green');
        }
    });

    modeWebcam.addEventListener('change', () => {
        if (modeWebcam.checked) {
            fileControls.classList.add('d-none');
            webcamControls.classList.remove('d-none');
            elBtnDownload.classList.add('d-none');
            resetDisplay();
            elProcessStatus.textContent = 'Status: Live Camera Ready';
            setSystemStatus('CAMERA READY', 'green');
        }
    });

    // -----------------------------------------------------------------------
    // VIDEO FILE PROCESSING
    // -----------------------------------------------------------------------
    elVideoUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        elFileName.textContent = file.name;
        elProcessStatus.textContent = 'Status: Uploading video...';
        setSystemStatus('UPLOADING FOOTAGE', 'blue');

        const formData = new FormData();
        formData.append('video', file);

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                uploadedFilename = data.filename;
                elBtnStart.disabled = false;
                elProcessStatus.textContent = 'Status: Video ready. Click Process.';
                setSystemStatus('READY TO PROCESS', 'green');
            } else {
                const errMsg = data.error || data.message || 'Upload failed';
                alert('Upload error: ' + errMsg);
                elProcessStatus.textContent = 'Status: ' + errMsg;
                setSystemStatus('UPLOAD ERROR', 'red');
            }
        } catch (err) {
            console.error('Upload error:', err);
            alert('Error connecting to backend server during video upload.');
            elProcessStatus.textContent = 'Status: Network error';
            setSystemStatus('NETWORK ERROR', 'red');
        }
    });

    elBtnStart.addEventListener('click', async () => {
        elBtnStart.disabled = true;

        // Hide video placeholder & stream, show loading overlay with d-flex
        elVideoPlaceholder.classList.remove('d-flex');
        elVideoPlaceholder.classList.add('d-none');
        elVideoStream.classList.add('d-none');

        elLoadingOverlay.classList.remove('d-none');
        elLoadingOverlay.classList.add('d-flex');

        elProcessStatus.textContent = 'Status: Running YOLO + Object Tracker...';
        setSystemStatus('AI INFERENCE ACTIVE', 'amber');

        try {
            const res = await fetch('/api/process/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: uploadedFilename })
            });

            const data = await res.json();
            
            // Hide loading overlay
            elLoadingOverlay.classList.remove('d-flex');
            elLoadingOverlay.classList.add('d-none');

            if (res.ok && data.status === 'success') {
                const summary = data.summary;
                updateStatsUI(summary);

                if (data.stream_url) {
                    elVideoStream.src = data.stream_url + '?t=' + new Date().getTime();
                    elVideoStream.classList.remove('d-none');
                    elVideoPlaceholder.classList.add('d-none');
                    elVideoPlaceholder.classList.remove('d-flex');
                    if (elOverlayBadges) elOverlayBadges.classList.remove('d-none');
                }

                if (data.download_url) {
                    elBtnDownload.href = data.download_url;
                    elBtnDownload.classList.remove('d-none');
                }

                elProcessStatus.textContent = 'Status: Processing Complete!';
                setSystemStatus('PROCESSING COMPLETE', 'green');
            } else {
                const errMsg = data.error || data.message || 'Processing failed';
                alert('Processing error: ' + errMsg);
                elVideoPlaceholder.classList.remove('d-none');
                elVideoPlaceholder.classList.add('d-flex');
                elProcessStatus.textContent = 'Status: ' + errMsg;
                setSystemStatus('PROCESSING FAILED', 'red');
            }
        } catch (err) {
            console.error('Processing error:', err);
            elLoadingOverlay.classList.remove('d-flex');
            elLoadingOverlay.classList.add('d-none');
            elVideoPlaceholder.classList.remove('d-none');
            elVideoPlaceholder.classList.add('d-flex');
            alert('Server error: Could not complete video processing.');
            elProcessStatus.textContent = 'Status: Server error';
            setSystemStatus('SERVER ERROR', 'red');
        } finally {
            elBtnStart.disabled = false;
        }
    });

    // -----------------------------------------------------------------------
    // LIVE WEBCAM PROCESSING
    // -----------------------------------------------------------------------
    elBtnWebcamStart.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/webcam/start', { method: 'POST' });
            const data = await res.json();

            if (res.ok && data.status === 'success') {
                elVideoStream.src = '/api/webcam/stream?t=' + Date.now();
                elVideoStream.classList.remove('d-none');
                elVideoPlaceholder.classList.add('d-none');
                elVideoPlaceholder.classList.remove('d-flex');
                if (elOverlayBadges) elOverlayBadges.classList.remove('d-none');

                elBtnWebcamStart.disabled = true;
                elBtnWebcamStop.disabled = false;

                elProcessStatus.textContent = 'Status: Live Camera Active';
                setSystemStatus('LIVE CAMERA ACTIVE', 'red');

                startWebcamStatsPolling();
            } else {
                const errMsg = data.error || data.message || 'Could not start webcam';
                alert('Webcam error: ' + errMsg);
            }
        } catch (err) {
            console.error('Webcam start error:', err);
            alert('Failed to connect to webcam feed on backend.');
        }
    });

    elBtnWebcamStop.addEventListener('click', () => {
        stopWebcamStream();
    });

    function stopWebcamStream() {
        fetch('/api/webcam/stop', { method: 'POST' }).catch(() => {});
        if (webcamPollTimer) {
            clearInterval(webcamPollTimer);
            webcamPollTimer = null;
        }
        resetDisplay();

        elBtnWebcamStart.disabled = false;
        elBtnWebcamStop.disabled = true;

        elProcessStatus.textContent = 'Status: Live Camera Stopped';
        setSystemStatus('CAMERA STOPPED', 'amber');
    }

    function startWebcamStatsPolling() {
        if (webcamPollTimer) clearInterval(webcamPollTimer);
        webcamPollTimer = setInterval(async () => {
            try {
                const res = await fetch('/api/webcam/summary');
                if (res.ok) {
                    const stats = await res.json();
                    if (stats && stats.status === 'live') {
                        updateStatsUI(stats);
                    }
                }
            } catch (e) {
                console.warn('Webcam stats poll error:', e);
            }
        }, 400);
    }

    function resetDisplay() {
        if (elLoadingOverlay) {
            elLoadingOverlay.classList.remove('d-flex');
            elLoadingOverlay.classList.add('d-none');
        }
        elVideoStream.src = '';
        elVideoStream.classList.add('d-none');
        elVideoPlaceholder.classList.remove('d-none');
        elVideoPlaceholder.classList.add('d-flex');
        elBtnDownload.classList.add('d-none');
        if (elOverlayBadges) elOverlayBadges.classList.add('d-none');
    }

    function setSystemStatus(text, color) {
        if (elStatusBadge) elStatusBadge.textContent = text;
        if (elStatusPulse) {
            elStatusPulse.className = 'pulse-dot ' + (color === 'red' ? 'bg-danger' : color === 'amber' ? 'bg-warning' : color === 'blue' ? 'bg-info' : 'green');
        }
    }

    initChart();
});

function updateStatsUI(summary) {
    const classCounts = summary.class_counts || {};

    let vehicleCount = 0;
    let roadUserCount = 0;
    let infraCount = 0;
    let hazardCount = 0;

    for (const [cls, count] of Object.entries(classCounts)) {
        const clsLower = cls.toLowerCase();
        if (CATEGORIES.vehicles.includes(clsLower)) vehicleCount += count;
        else if (CATEGORIES.road_users.includes(clsLower)) roadUserCount += count;
        else if (CATEGORIES.infrastructure.includes(clsLower)) infraCount += count;
        else if (CATEGORIES.road_hazards.includes(clsLower)) hazardCount += count;
    }

    const totalUnique = summary.total_unique_objects ?? (vehicleCount + roadUserCount + infraCount + hazardCount);
    const totalRaw = summary.total_raw_detections ?? summary.total_detections ?? totalUnique;

    document.getElementById('stat-total-unique').textContent = totalUnique;
    document.getElementById('stat-total-raw-desc').textContent = `Persistent Track IDs assigned (${totalRaw} total frame detections)`;

    document.getElementById('stat-vehicles').textContent = vehicleCount;
    document.getElementById('stat-road-users').textContent = roadUserCount;
    document.getElementById('stat-infrastructure').textContent = infraCount;
    document.getElementById('stat-hazards').textContent = hazardCount;

    document.getElementById('stat-frames').textContent = summary.frames_processed ?? 0;
    document.getElementById('stat-fps').textContent = (summary.average_fps ?? 0) + ' FPS';
    document.getElementById('stat-time').textContent = (summary.elapsed_seconds ?? 0) + 's';

    updateChart(classCounts);
}

function initChart() {
    const ctx = document.getElementById('object-chart')?.getContext('2d');
    if (!ctx) return;

    objectChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Unique Count',
                data: [],
                backgroundColor: 'rgba(255, 183, 3, 0.85)',
                borderColor: '#ffb703',
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: '#f1f5f9', font: { family: 'Plus Jakarta Sans', size: 11, weight: 'bold' } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    ticks: { color: '#f1f5f9', precision: 0, font: { family: 'Plus Jakarta Sans', weight: 'bold' } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    beginAtZero: true
                }
            }
        }
    });
}

function updateChart(classCounts) {
    if (!objectChart) return;
    const labels = Object.keys(classCounts).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const data   = Object.values(classCounts);

    objectChart.data.labels = labels;
    objectChart.data.datasets[0].data = data;
    objectChart.update();
}
