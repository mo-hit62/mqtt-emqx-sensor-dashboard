const client = mqtt.connect("ws://localhost:8083/mqtt");

// ============================================================
// DOM ELEMENTS
// ============================================================

const temperatureElement = document.getElementById("temperature");
const humidityElement = document.getElementById("humidity");
const lightElement = document.getElementById("light");
const aqiElement = document.getElementById("aqi");
const batteryElement = document.getElementById("battery");

const statusElement = document.getElementById("status");

const deviceElement = document.getElementById("device");
const locationElement = document.getElementById("location");

const messageCountElement =
    document.getElementById("messageCount");

const lastUpdateElement =
    document.getElementById("lastUpdate");

const aiStatusElement =
    document.getElementById("aiStatus");

const anomalyCountElement =
    document.getElementById("anomalyCount");

const latestEventElement =
    document.getElementById("latestEvent");

const aiActionElement =
    document.getElementById("aiAction");


// ============================================================
// STATE
// ============================================================

let messageCount = 0;
let anomalyCount = 0;

let temperatureData = [];
let humidityData = [];
let labels = [];


// ============================================================
// CHART
// ============================================================

const ctx = document.getElementById("sensorChart");

const sensorChart = new Chart(ctx, {

    type: "line",

    data: {

        labels: labels,

        datasets: [

            {
                label: "Temperature (°C)",
                data: temperatureData,
                borderColor: "#38bdf8",
                backgroundColor: "rgba(56,189,248,0.12)",
                borderWidth: 2,
                tension: 0.35,
                pointRadius: 2,
                fill: false
            },

            {
                label: "Humidity (%)",
                data: humidityData,
                borderColor: "#fb7185",
                backgroundColor: "rgba(251,113,133,0.12)",
                borderWidth: 2,
                tension: 0.35,
                pointRadius: 2,
                fill: false
            }

        ]

    },

    options: {

        responsive: true,
        maintainAspectRatio: false,

        animation: {
            duration: 500
        },

        plugins: {

            legend: {
                labels: {
                    color: "#d1d5db"
                }
            }

        },

        scales: {

            x: {
                ticks: {
                    color: "#64748b"
                },

                grid: {
                    color: "rgba(100,116,139,0.12)"
                }
            },

            y: {
                ticks: {
                    color: "#64748b"
                },

                grid: {
                    color: "rgba(100,116,139,0.12)"
                }
            }

        }

    }

});


// ============================================================
// MQTT CONNECT
// ============================================================

client.on("connect", function () {

    statusElement.textContent = "Connected";
    statusElement.style.color = "#34d399";

    console.log("Connected to EMQX");


    // Combined telemetry stream
    client.subscribe(
        "sensors/+/telemetry",
        function (error) {

            if (error) {
                console.error(
                    "Telemetry subscription failed:",
                    error
                );
            } else {
                console.log(
                    "Subscribed to telemetry"
                );
            }

        }
    );


    // AI alerts
    client.subscribe(
        "sensors/+/alerts",
        function (error) {

            if (error) {
                console.error(
                    "Alert subscription failed:",
                    error
                );
            } else {
                console.log(
                    "Subscribed to AI alerts"
                );
            }

        }
    );

});


// ============================================================
// MQTT MESSAGE
// ============================================================

client.on("message", function (topic, message) {

    let data;

    try {

        data = JSON.parse(
            message.toString()
        );

    } catch (error) {

        console.error(
            "Invalid JSON received:",
            error
        );

        return;
    }


    // ========================================================
    // TELEMETRY
    // ========================================================

    if (topic.includes("/telemetry")) {

        messageCount++;

        const temperature =
            Number(data.temperature);

        const humidity =
            Number(data.humidity);

        const light =
            Number(data.light);

        const aqi =
            Number(data.aqi);

        const battery =
            Number(data.battery);


        // -----------------------------
        // SENSOR VALUES
        // -----------------------------

        if (temperatureElement) {
            temperatureElement.textContent =
                temperature.toFixed(2) + " °C";
        }

        if (humidityElement) {
            humidityElement.textContent =
                humidity.toFixed(2) + " %";
        }

        if (lightElement) {
            lightElement.textContent =
                Math.round(light) + " lux";
        }

        if (aqiElement) {
            aqiElement.textContent =
                Math.round(aqi);
        }

        if (batteryElement) {
            batteryElement.textContent =
                battery.toFixed(1) + "%";
        }


        // -----------------------------
        // DEVICE INFORMATION
        // -----------------------------

        if (deviceElement) {
            deviceElement.textContent =
                data.device_id || "SENSOR_001";
        }

        if (locationElement) {
            locationElement.textContent =
                data.location || "Room_A";
        }


        // -----------------------------
        // MESSAGE COUNT
        // -----------------------------

        if (messageCountElement) {

            messageCountElement.textContent =
                messageCount;
        }


        // -----------------------------
        // LAST UPDATE
        // -----------------------------

        if (lastUpdateElement) {

            lastUpdateElement.textContent =
                new Date().toLocaleTimeString();
        }


        // -----------------------------
        // AI STATUS
        // -----------------------------

        if (aiStatusElement) {

            if (data.ai_status === "RESOLVED") {

                aiStatusElement.textContent =
                    "✓ ANOMALY RESOLVED";

                aiStatusElement.style.color =
                    "#34d399";

            } else {

                aiStatusElement.textContent =
                    "✓ NORMAL";

                aiStatusElement.style.color =
                    "#34d399";
            }
        }


        // -----------------------------
        // ANOMALY COUNT
        // -----------------------------

        if (
            typeof data.anomalies_detected ===
            "number"
        ) {

            anomalyCount =
                data.anomalies_detected;

            if (anomalyCountElement) {

                anomalyCountElement.textContent =
                    anomalyCount;
            }
        }


        // -----------------------------
        // AI ACTION
        // -----------------------------

        if (aiActionElement) {

            if (
                data.ai_action ===
                "AUTOMATIC_CORRECTION"
            ) {

                aiActionElement.textContent =
                    "Automatic corrective response";

            } else {

                aiActionElement.textContent =
                    "Continuous monitoring";
            }
        }


        // -----------------------------
        // CHART DATA
        // -----------------------------

        const time =
            new Date().toLocaleTimeString();

        labels.push(time);

        temperatureData.push(temperature);
        humidityData.push(humidity);


        // Keep last 30 readings
        if (labels.length > 30) {

            labels.shift();
            temperatureData.shift();
            humidityData.shift();
        }


        sensorChart.update();
    }


    // ========================================================
    // AI ALERT
    // ========================================================

    if (topic.includes("/alerts")) {

        console.log(
            "AI ALERT:",
            data
        );


        if (data.event === "ANOMALY_DETECTED") {

            if (latestEventElement) {

                latestEventElement.textContent =
                    data.reason ||
                    "UNUSUAL_SENSOR_PATTERN";
            }


            if (aiStatusElement) {

                aiStatusElement.textContent =
                    "⚠ ANOMALY DETECTED";

                aiStatusElement.style.color =
                    "#fb7185";
            }

            if (aiActionElement) {

                aiActionElement.textContent =
                    "AI corrective action in progress";

            }
        }
    }

});


// ============================================================
// MQTT ERROR
// ============================================================

client.on("error", function (error) {

    console.error(
        "MQTT connection error:",
        error
    );

    statusElement.textContent =
        "Connection Error";

    statusElement.style.color =
        "#fb7185";
});


// ============================================================
// MQTT CLOSE
// ============================================================

client.on("close", function () {

    statusElement.textContent =
        "Disconnected";

    statusElement.style.color =
        "#fb7185";
});
