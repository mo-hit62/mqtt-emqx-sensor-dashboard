# MQTT EMQX Sensor Dashboard

A real-time IoT sensor dashboard built using Python, MQTT, EMQX, MQTT over WebSocket, HTML, and JavaScript.

The project continuously generates temperature and humidity sensor values using Python, publishes them to an EMQX MQTT broker, and displays the received values live on a web dashboard.

## Project Architecture

```text
Python Sensor Publisher
        |
        | MQTT Publish
        v
   EMQX MQTT Broker
        |
        | MQTT over WebSocket
        v
     Web Browser
        |
        v
      app.js
        |
        v
    index.html
        |
        v
Live Temperature & Humidity Dashboard
