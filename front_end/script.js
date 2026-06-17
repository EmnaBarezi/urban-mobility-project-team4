// API BASE URL

const API_BASE = "http://127.0.0.1:5000/api";


const charts = {};

let map = null;
let geojsonLayer = null;
let geojsonCache = null; 

// ------------------------------------------------------------
// Helpers
// ------------------------------------------------------------

function destroyChart(key) {
    if (charts[key]) {
        charts[key].destroy();
        delete charts[key];
    }
}

// Builds borough [start-end] from the current filter controls
function filterQuery(extra = {}) {
    const params = new URLSearchParams();
    const borough = document.getElementById("boroughFilter").value;
    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;

    if (borough) params.set("borough", borough);
    if (start) params.set("start", start);
    if (end) params.set("end", end);

    Object.entries(extra).forEach(([k, v]) => params.set(k, v));

    const str = params.toString();
    return str ? "?" + str : "";
}

async function apiGet(path, extra = {}) {
    const res = await fetch(API_BASE + path + filterQuery(extra));
    if (!res.ok) throw new Error(`${path} returned ${res.status}`);
    return res.json();
}

function showBanner(message, isError = false) {
    const el = document.getElementById("loadingBanner");
    el.textContent = message;
    el.classList.remove("hidden");
    el.classList.toggle("error", isError);
}

function hideBanner() {
    document.getElementById("loadingBanner").classList.add("hidden");
}

// ======================
// KPI Cards
// ======================

async function loadKPIs() {
    const data = await apiGet("/kpis");

    document.getElementById("totalTrips").textContent =
        data.totalTrips.toLocaleString();

    document.getElementById("avgFare").textContent =
        "$" + data.avgFare.toFixed(2);

    document.getElementById("avgDistance").textContent =
        data.avgDistance.toFixed(1);

    document.getElementById("avgSpeed").textContent =
        data.avgSpeed.toFixed(1);

} 
    
// ======================
// Hourly demand chart
// ======================

async function loadHourlyChart() {
    const data = await apiGet("/hourly-demand");
    destroyChart("hourly");

    charts.hourly = new Chart(
        document.getElementById("hourlyTripsChart"),
        {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Trips",
                    data: data.data,
                    borderColor: "#3DD6C4",
                    backgroundColor: "rgba(61, 214, 196, 0.12)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: chartOptions("line")
        }
    );

} 

// ============================
// Revenue by Borough chart
// ============================

async function loadRevenueChart() {
    const data = await apiGet("/revenue-by-borough");
    destroyChart("revenue");

    charts.revenue = new Chart(
        document.getElementById("revenueChart"),
        {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Revenue",
                    data: data.data,
                    backgroundColor: "#F5c518",
                    borderRadius: 4
                }]
            },
            options: chartOptions("bar")
        }
    );
}

// ======================
// Speed by hour chart
// ======================

async function loadSpeedChart() {
    const data = await apiGet("/speed-by-hour");
    destroyChart("speed");

    charts.speed = new Chart(
        document.getElementById("speedChart"),
        {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Speed (mph) ",
                    data: data.data,
                    borderColor: "#9B8CFF",
                    backgroundColor: "rgba(155, 140, 255, 0.12)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },            
            options: chartOptions("line")
        }
    );
}

// ======================
// Top routes chart
// ======================

async function loadRoutesChart() {
    const data = await apiGet("/top-routes");
    destroyChart("routes");

    charts.routes = new Chart(
        document.getElementById("routesChart"),
        {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Trips",
                    data: data.data,
                    backgroundColor: "#F2684B",
                    borderRadius: 4
                }]
            },
            options: { ...chartOptions("bar"), indexAxis: "y" }
        }
    );
} 

// ---------------------
// Chart.js theme
// ---------------------

function chartOptions(type) {
    const gridColor = "#232938";
    const textColor = "#8890A2";

    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "#171C26",
                borderColor: "#2E3648",
                borderWidth: 1,
                titleColor: "#E8EAED",
                bodyColor: "#E8EAED",
                padding: 10
            }
        },
        scales: {
            x: {
                grid: { color: type === "bar" && document.body ? "transparent" : gridColor, display: false },
                ticks: { color: textColor, font: { size: 11 } }
            },
            y: {
                grid: { color: gridColor },
                ticks: { color: textColor, font: { size: 11 } },
                beginAtZero: true
            }
        }
    };
}

// -------------------------------
// Borough filter dropdown 
// ------------------------------

async function loadBoroughOptions() {
    try {
        const boroughs = await apiGet("/boroughs");
        const select = document.getElementById("boroughFilter");
        boroughs.forEach(b => {
            const opt = document.createElement("option");
            opt.value = b;
            opt.textContent = b;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to load borough list:", err);
    }
}

// -------------------------------
// Map; taxi zone boundaries
// -------------------------------

function initMap() {
    map = L.map("map").setView([40.7128, -74.0060], 11);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
}

function zoneColor(count, max) {
    if (!max || !count) return "#1A2030";
    const ratio = count / max;
    if (ratio > 0.8) return "#F5C518";
    if (ratio > 0.6) return "#D9AE17";
    if (ratio > 0.4) return "#3DD6C4";
    if (ratio > 0.2) return "#2BA396";
    return "#1A2030";
}

async function loadMap() {
    const zoneStats = await apiGet("/zone-stats");

    if (!geojsonCache) {
        try {
            geojsonCache = await apiGet("/taxi-zones-geojson");
        } catch (err) {
            console.error("Could not load taxi zone boundaries:", err);
            return;
        }
    }

    if (geojsonLayer) {
        map.removeLayer(geojsonLayer);
        geojsonLayer = null;
    }

    const lookup = {};
    let max = 0;
    zoneStats.forEach(z => {
        lookup[z.locationId] = z.tripCount;
        if (z.tripCount > max) max = z.tripCount;
    });

    geojsonLayer = L.geoJSON(geojsonCache, {
        style: feature => ({
            fillColor: zoneColor(lookup[feature.properties.LocationID], max),
            fillOpacity: 0.75,
            color: "#0B0E14",
            weight: 0.6
        }),
        onEachFeature: (feature, layer) => {
            const id = feature.properties.LocationID;
            const name = feature.properties.zone || "Unknown zone";
            const count = lookup[id] || 0;
            layer.bindPopup(
                `<strong>${name}</strong><br>Pickups: ${count.toLocaleString()}`
            );
        }
    }).addTo(map);
}

// ------------------------------------------------------------
// Connection status indicator (sidebar footer)
// ------------------------------------------------------------

async function checkHealth() {
    const dot = document.getElementById("dbStatus");
    const text = document.getElementById("dbStatusText");
    try {
        const res = await fetch(API_BASE + "/kpis");
        if (res.ok) {
            dot.className = "status-dot ok";
            text.textContent = "API connected";
            return true;
        }
        throw new Error("Bad response");
    } catch {
        dot.className = "status-dot error";
        text.textContent = "API offline";
        return false;
    }
}

// -----------------------------------
// Load everything on page load
// -----------------------------------

async function loadDashboard() {
    showBanner("Loading data…");

    const ok = await checkHealth();
    if (!ok) {
        showBanner("Cannot reach the API. Run: python backend/app.py", true);
        return;
    }

    try {
        await Promise.all([
            loadKPIs(),
            loadHourlyChart(),
            loadRevenueChart(),
            loadSpeedChart(),
            loadRoutesChart(),
            loadMap()
        ]);
        hideBanner();
    } catch (err) {
        console.error("Dashboard load error:", err);
        showBanner("Something went wrong loading the dashboard. Check the console.", true);
    }
}

// --------------------------------------
// Sidebar nav; active-state toggle
// --------------------------------------

document.querySelectorAll(".sidebar li").forEach(li => {
    li.addEventListener("click", () => {
        document.querySelectorAll(".sidebar li").forEach(x => x.classList.remove("active"));
        li.classList.add("active");
    });
});

// -----------------------------
// Filter button
// -----------------------------

document.getElementById("applyFilters").addEventListener("click", loadDashboard);

initMap();
loadBoroughOptions();
loadDashboard();
