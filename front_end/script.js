// API BASE URL

const API_BASE = "http://127.0.0.1:5000/api";

// ------------------------------------------------------------
// Helpers
// ------------------------------------------------------------

function destroyChart(key) {
    if (charts[key]) {
        charts[key].destroy();
        delete charts[key];
    }
}

// Builds ?borough=&start=&end= from the current filter controls
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
// KPI CARDS
// ======================

async function loadKPIs() {
    try {
        const res = await fetch(`${API_BASE}/kpis`);
        const data = await res.json();

        document.getElementById("totalTrips").textContent =
            data.totalTrips.toLocaleString();

        document.getElementById("avgFare").textContent =
            "$" + data.avgFare.toFixed(2);

        document.getElementById("avgDistance").textContent =
            data.avgDistance.toFixed(1);

        document.getElementById("avgSpeed").textContent =
            data.avgSpeed.toFixed(1);

    } catch (err) {
        console.error("Failed to load KPIs:", err);
    }
}

// ======================
// HOURLY DEMAND CHART
// ======================

async function loadHourlyChart() {
    try {
        const res = await fetch(`${API_BASE}/hourly-demand`);
        const data = await res.json();

        new Chart(
            document.getElementById("hourlyTripsChart"),
            {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Trips",
                        data: data.data,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.15)",
                        fill: true,
                        tension: 0.3
                    }]
                }
            }
        );

    } catch (err) {
        console.error("Failed to load hourly demand chart:", err);
    }
}

// ======================
// REVENUE CHART
// ======================

async function loadRevenueChart() {
    try {
        const res = await fetch(`${API_BASE}/revenue-by-borough`);
        const data = await res.json();

        new Chart(
            document.getElementById("revenueChart"),
            {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Revenue",
                        data: data.data,
                        backgroundColor: "#2563eb"
                    }]
                }
            }
        );

    } catch (err) {
        console.error("Failed to load revenue chart:", err);
    }
}

// ======================
// SPEED CHART
// ======================

async function loadSpeedChart() {
    try {
        const res = await fetch(`${API_BASE}/speed-by-hour`);
        const data = await res.json();

        new Chart(
            document.getElementById("speedChart"),
            {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Speed",
                        data: data.data,
                        borderColor: "#06b6d4",
                        backgroundColor: "rgba(6, 182, 212, 0.15)",
                        fill: true,
                        tension: 0.3
                    }]
                }
            }
        );

    } catch (err) {
        console.error("Failed to load speed chart:", err);
    }
}

// ======================
// ROUTES CHART
// ======================

async function loadRoutesChart() {
    try {
        const res = await fetch(`${API_BASE}/top-routes`);
        const data = await res.json();

        new Chart(
            document.getElementById("routesChart"),
            {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Trips",
                        data: data.data,
                        backgroundColor: "#8b5cf6"
                    }]
                }
            }
        );

    } catch (err) {
        console.error("Failed to load routes chart:", err);
    }
}

// ======================
// MAP
// ======================

const map = L.map("map").setView(
    [40.7128, -74.0060],
    11
);

L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19
    }
).addTo(map);

L.marker(
    [40.7580, -73.9855]
)
.addTo(map)
.bindPopup("Times Square");

// ======================
// LOAD EVERYTHING ON PAGE LOAD
// ======================

loadKPIs();
loadHourlyChart();
loadRevenueChart();
loadSpeedChart();
loadRoutesChart();

// ======================
// APPLY FILTERS BUTTON
// (currently just reloads all charts — filtering by
//  borough/date isn't wired into the API yet)
// ======================

document.querySelector(".filters button").addEventListener("click", () => {
    loadKPIs();
    loadHourlyChart();
    loadRevenueChart();
    loadSpeedChart();
    loadRoutesChart();
});