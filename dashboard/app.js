const client = mqtt.connect("ws://localhost:8083/mqtt");

const temperatureElement = document.getElementById("temperature");
const humidityElement = document.getElementById("humidity");
const statusElement = document.getElementById("status");

client.on("connect", function () {
    statusElement.textContent = "Connected";
    statusElement.style.color = "green";

    console.log("Connected to EMQX");

    client.subscribe("sensors/temperature", function (error) {
        if (error) {
            console.error("Temperature subscription failed:", error);
        } else {
            console.log("Subscribed to temperature");
        }
    });

    client.subscribe("sensors/humidity", function (error) {
        if (error) {
            console.error("Humidity subscription failed:", error);
        } else {
            console.log("Subscribed to humidity");
        }
    });
});

client.on("message", function (topic, message) {

    const value = message.toString();

    if (topic === "sensors/temperature") {
        temperatureElement.textContent = value + " °C";
    }

    if (topic === "sensors/humidity") {
        humidityElement.textContent = value + " %";
    }
});

client.on("error", function (error) {
    console.error("MQTT connection error:", error);
    statusElement.textContent = "Connection Error";
});

client.on("close", function () {
    statusElement.textContent = "Disconnected";
    statusElement.style.color = "red";
});
