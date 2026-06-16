// ======================
// KPI CARDS
// ======================

const dashboardStats = {
    totalTrips: 421568,
    avgFare: 17.85,
    avgDistance: 3.9,
    avgSpeed: 14.2
};

document.getElementById("totalTrips").textContent =
    dashboardStats.totalTrips.toLocaleString();

document.getElementById("avgFare").textContent =
    "$" + dashboardStats.avgFare.toFixed(2);

document.getElementById("avgDistance").textContent =
    dashboardStats.avgDistance.toFixed(1);

document.getElementById("avgSpeed").textContent =
    dashboardStats.avgSpeed.toFixed(1);

// ======================
// HOURLY DEMAND CHART
// ======================

new Chart(
    document.getElementById("hourlyTripsChart"),
    {
        type: "line",
        data: {
            labels: [
                "0","1","2","3","4","5",
                "6","7","8","9","10","11",
                "12","13","14","15","16",
                "17","18","19","20","21",
                "22","23"
            ],
            datasets: [{
                label: "Trips",
                data: [
                    120,90,70,50,40,80,
                    250,500,850,900,
                    780,720,690,710,
                    750,820,950,
                    1100,1200,1000,
                    850,650,400,250
                ]
            }]
        }
    }
);

// ======================
// REVENUE CHART
// ======================

new Chart(
    document.getElementById("revenueChart"),
    {
        type: "bar",
        data: {
            labels: [
                "Manhattan",
                "Queens",
                "Brooklyn",
                "Bronx"
            ],
            datasets: [{
                label: "Revenue",
                data: [
                    520000,
                    310000,
                    210000,
                    90000
                ]
            }]
        }
    }
);

// ======================
// SPEED CHART
// ======================

new Chart(
    document.getElementById("speedChart"),
    {
        type: "line",
        data: {
            labels: [
                "0","1","2","3","4","5",
                "6","7","8","9","10","11",
                "12","13","14","15","16",
                "17","18","19","20","21",
                "22","23"
            ],
            datasets: [{
                label: "Speed",
                data: [
                    24,23,22,21,20,18,
                    15,12,10,11,13,14,
                    13,12,12,11,10,9,
                    10,12,14,17,20,22
                ]
            }]
        }
    }
);

// ======================
// ROUTES CHART
// ======================

new Chart(
    document.getElementById("routesChart"),
    {
        type: "bar",
        data: {
            labels: [
                "Queens → Manhattan",
                "Brooklyn → Manhattan",
                "Manhattan → Queens",
                "Bronx → Manhattan"
            ],
            datasets: [{
                label: "Trips",
                data: [
                    12500,
                    9500,
                    8700,
                    6400
                ]
            }]
        }
    }
);

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