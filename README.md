# MQTT EMQX Sensor Dashboard

A real-time IoT sensor dashboard built using Python, MQTT, EMQX, MQTT over WebSocket, HTML, and JavaScript.

The project continuously generates temperature and humidity sensor values using Python, publishes them to an EMQX MQTT broker, and displays the received values live on a web dashboard.

## Project Architecture

Python Sensor Publisher  
↓  
MQTT Publish  
↓  
EMQX MQTT Broker  
↓  
MQTT over WebSocket  
↓  
Web Browser → app.js → index.html  
↓  
Live Temperature & Humidity Dashboard

## How It Works

1. `publisher.py` generates temperature and humidity values continuously.
2. The Python program publishes the values to MQTT topics.
3. EMQX receives the MQTT messages as the broker.
4. The web dashboard connects to EMQX using MQTT over WebSocket.
5. `app.js` subscribes to the temperature and humidity topics.
6. Incoming messages are displayed live in the dashboard.

## MQTT Topics

- `sensors/temperature`
- `sensors/humidity`

## Technologies Used

- Python
- MQTT
- EMQX
- MQTT over WebSocket
- HTML
- JavaScript

## Project Structure

```text
mqtt-emqx-sensor-dashboard/
├── dashboard/
│   ├── app.js
│   └── index.html
├── screenshots/
│   ├── mqtt_dashboard.png
│   ├── emqx_websocket_subscriptions.png
│   └── emqx_received_messages.png
├── publisher.py
├── README.md
└── .gitignore
