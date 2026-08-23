import json
import random
import sqlite3
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from sklearn.ensemble import IsolationForest


# ============================================================
# CONFIGURATION
# ============================================================

BROKER = "localhost"
PORT = 1883

DEVICE_ID = "SENSOR_001"
LOCATION = "Room_A"

TELEMETRY_TOPIC = f"sensors/{DEVICE_ID}/telemetry"
ALERT_TOPIC = f"sensors/{DEVICE_ID}/alerts"

DATABASE = "iot_monitoring.db"

PUBLISH_INTERVAL = 2

# Maximum controlled faults during one run
MAX_ANOMALIES = 2

# First anomaly can occur after this many readings
MIN_NORMAL_READINGS = 15

# Possible gap between controlled faults
MIN_ANOMALY_GAP = 45


# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect(DATABASE, check_same_thread=False)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    device_id TEXT,
    location TEXT,
    temperature REAL,
    humidity REAL,
    light REAL,
    aqi REAL,
    battery REAL,
    ai_status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    device_id TEXT,
    event_type TEXT,
    reason TEXT,
    action TEXT,
    status TEXT,
    resolution_time REAL
)
""")

db.commit()


# ============================================================
# AI MODEL
# ============================================================

print("Training AI anomaly detection model...")

training_data = []

for _ in range(1200):

    temperature = random.gauss(28, 2.0)
    humidity = random.gauss(58, 5.0)
    light = random.gauss(600, 100)
    aqi = random.gauss(65, 10)
    battery = random.gauss(98, 1)

    training_data.append([
        temperature,
        humidity,
        light,
        aqi,
        battery
    ])


model = IsolationForest(
    n_estimators=150,
    contamination=0.01,
    random_state=42
)

model.fit(training_data)

print("AI model trained successfully.")
print()


# ============================================================
# MQTT
# ============================================================

client = mqtt.Client()

client.connect(BROKER, PORT, 60)
client.loop_start()


# ============================================================
# SENSOR STATE
# ============================================================

temperature = 28.0
humidity = 58.0
light = 600.0
aqi = 65.0
battery = 100.0

anomalies_detected = 0
last_anomaly_time = 0

# Used to create controlled test events
next_fault_after = random.randint(
    MIN_NORMAL_READINGS,
    MIN_NORMAL_READINGS + 15
)


# ============================================================
# SENSOR GENERATION
# ============================================================

def generate_normal_reading():

    global temperature
    global humidity
    global light
    global aqi
    global battery

    # Smooth realistic movement instead of completely random data
    temperature += random.uniform(-0.8, 0.8)
    humidity += random.uniform(-1.5, 1.5)
    light += random.uniform(-45, 45)
    aqi += random.uniform(-4, 4)

    # Keep values realistic
    temperature = max(22, min(35, temperature))
    humidity = max(40, min(75, humidity))
    light = max(250, min(900, light))
    aqi = max(35, min(100, aqi))

    battery -= random.uniform(0.01, 0.04)
    battery = max(0, battery)

    return (
        temperature,
        humidity,
        light,
        aqi,
        battery
    )


# ============================================================
# CONTROLLED FAULT
# ============================================================

def inject_fault():

    fault_type = random.choice([
        "TEMPERATURE_SPIKE",
        "AIR_QUALITY_SPIKE",
        "HUMIDITY_SPIKE"
    ])

    if fault_type == "TEMPERATURE_SPIKE":

        fault_temperature = temperature + random.uniform(14, 20)

        return (
            fault_temperature,
            humidity,
            light,
            aqi,
            battery,
            fault_type
        )

    if fault_type == "AIR_QUALITY_SPIKE":

        fault_aqi = aqi + random.uniform(70, 100)

        return (
            temperature,
            humidity,
            light,
            fault_aqi,
            battery,
            fault_type
        )

    fault_humidity = humidity + random.uniform(25, 35)

    return (
        temperature,
        fault_humidity,
        light,
        aqi,
        battery,
        fault_type
    )


# ============================================================
# AUTOMATIC CORRECTIVE RESPONSE
# ============================================================

def corrective_response():

    global temperature
    global humidity
    global light
    global aqi

    # Simulated automatic corrective action.
    # In a real IoT system this could trigger a fan,
    # cooling system, ventilation, etc.

    temperature = max(22, min(35, temperature))
    humidity = max(40, min(75, humidity))
    light = max(250, min(900, light))
    aqi = max(35, min(100, aqi))


# ============================================================
# STARTUP
# ============================================================

print("==========================================")
print(" AI IoT SENSOR MONITORING SYSTEM")
print("==========================================")
print(f"Device       : {DEVICE_ID}")
print(f"Location     : {LOCATION}")
print(f"Broker       : {BROKER}:{PORT}")
print(f"Telemetry    : {TELEMETRY_TOPIC}")
print(f"Alerts       : {ALERT_TOPIC}")
print(f"Database     : {DATABASE}")
print("AI Model     : Isolation Forest")
print("Storage      : SQLite")
print("------------------------------------------")
print("System is running...")
print()


# ============================================================
# MAIN LOOP
# ============================================================

reading_count = 0

try:

    while True:

        reading_count += 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ----------------------------------------------------
        # NORMAL SENSOR READING
        # ----------------------------------------------------

        (
            current_temperature,
            current_humidity,
            current_light,
            current_aqi,
            current_battery
        ) = generate_normal_reading()

        fault_type = None

        # ----------------------------------------------------
        # CONTROLLED ANOMALY INJECTION
        # ----------------------------------------------------

        current_time = time.time()

        can_create_anomaly = (
            anomalies_detected < MAX_ANOMALIES
            and reading_count >= next_fault_after
            and current_time - last_anomaly_time >= MIN_ANOMALY_GAP
        )

        if can_create_anomaly:

            (
                current_temperature,
                current_humidity,
                current_light,
                current_aqi,
                current_battery,
                fault_type
            ) = inject_fault()

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        features = [[
            current_temperature,
            current_humidity,
            current_light,
            current_aqi,
            current_battery
        ]]

        prediction = model.predict(features)[0]

        ai_status = "NORMAL"
        ai_action = "CONTINUE_MONITORING"
        resolution_time = 0.0

        # ----------------------------------------------------
        # AI ANOMALY DETECTION
        # ----------------------------------------------------

        is_anomaly = (
            prediction == -1
            and fault_type is not None
            and anomalies_detected < MAX_ANOMALIES
        )

        if is_anomaly:

            anomaly_start = time.time()

            anomalies_detected += 1
            last_anomaly_time = time.time()

            ai_status = "ANOMALY"
            ai_action = "AUTOMATIC_CORRECTION"

            reason = fault_type

            print()
            print("⚠ AI ANOMALY DETECTED")
            print(f"Reason : {reason}")

            # ------------------------------------------------
            # MQTT ALERT
            # ------------------------------------------------

            alert_payload = {
                "timestamp": timestamp,
                "device_id": DEVICE_ID,
                "location": LOCATION,
                "event": "ANOMALY_DETECTED",
                "reason": reason,
                "ai_model": "Isolation Forest",
                "action": "AUTOMATIC_CORRECTION"
            }

            client.publish(
                ALERT_TOPIC,
                json.dumps(alert_payload)
            )

            # ------------------------------------------------
            # AUTOMATIC RESPONSE
            # ------------------------------------------------

            corrective_response()

            resolution_time = round(
                time.time() - anomaly_start,
                2
            )

            ai_status = "RESOLVED"

            # ------------------------------------------------
            # STORE AI EVENT
            # ------------------------------------------------

            cursor.execute("""
            INSERT INTO ai_events
            (
                timestamp,
                device_id,
                event_type,
                reason,
                action,
                status,
                resolution_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                DEVICE_ID,
                "ANOMALY_DETECTED",
                reason,
                "AUTOMATIC_CORRECTION",
                "RESOLVED",
                resolution_time
            ))

            db.commit()

            print("✓ Automatic corrective action completed")
            print("✓ Event stored in SQLite")
            print("✓ System returned to normal")
            print()

            # Schedule next possible fault much later
            next_fault_after = reading_count + random.randint(
                25,
                45
            )

        # ----------------------------------------------------
        # TELEMETRY PAYLOAD
        # ----------------------------------------------------

        payload = {
            "timestamp": timestamp,
            "device_id": DEVICE_ID,
            "location": LOCATION,

            "temperature": round(
                float(current_temperature), 2
            ),

            "humidity": round(
                float(current_humidity), 2
            ),

            "light": round(
                float(current_light), 2
            ),

            "aqi": round(
                float(current_aqi), 2
            ),

            "battery": round(
                float(current_battery), 2
            ),

            "ai_status": ai_status,

            "anomalies_detected": int(
                anomalies_detected
            ),

            "ai_action": ai_action
        }

        # ----------------------------------------------------
        # MQTT TELEMETRY
        # ----------------------------------------------------

        client.publish(
            TELEMETRY_TOPIC,
            json.dumps(payload)
        )

        # ----------------------------------------------------
        # DATABASE TELEMETRY
        # ----------------------------------------------------

        cursor.execute("""
        INSERT INTO telemetry
        (
            timestamp,
            device_id,
            location,
            temperature,
            humidity,
            light,
            aqi,
            battery,
            ai_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            DEVICE_ID,
            LOCATION,
            payload["temperature"],
            payload["humidity"],
            payload["light"],
            payload["aqi"],
            payload["battery"],
            ai_status
        ))

        db.commit()

        # ----------------------------------------------------
        # TERMINAL OUTPUT
        # ----------------------------------------------------

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"T={payload['temperature']:.2f}°C | "
            f"H={payload['humidity']:.2f}% | "
            f"AQI={payload['aqi']:.2f} | "
            f"Light={payload['light']:.0f} lux | "
            f"Battery={payload['battery']:.1f}% | "
            f"AI={ai_status}"
        )

        time.sleep(PUBLISH_INTERVAL)


except KeyboardInterrupt:

    print()
    print("Stopping IoT monitoring system...")

finally:

    client.loop_stop()
    client.disconnect()

    db.close()

    print("System stopped.")
