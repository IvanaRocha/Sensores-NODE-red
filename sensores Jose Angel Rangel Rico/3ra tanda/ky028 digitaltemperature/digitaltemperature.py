from umqtt.simple import MQTTClient
from machine import Pin, SoftI2C
import time
import ssd1306
import json

# Configuración de la red WiFi
ssid = "Angel"
password = "12345678"

# Configuración del broker MQTT
mqtt_broker = "192.168.43.27"
mqtt_topic_distance = "utng/arg/sound"

# Configuración de los pines del sensor ultrasónico HC-SR04
pin_trigger = Pin(15, Pin.OUT)
pin_echo = Pin(16, Pin.IN)

# Límite de distancia en centímetros
distance_limit = 50.0  # Ejemplo: si la distancia medida supera los 50 cm, se enviará "True"

# Configuración del display OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def connect_wifi():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Conectando a WiFi...")
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    print("Conexión WiFi exitosa")

def connect_mqtt():
    client = MQTTClient("esp32", mqtt_broker)
    client.connect()
    print("Conexión MQTT exitosa")
    return client

def trigger_pulse():
    pin_trigger.value(1)
    time.sleep_us(10)
    pin_trigger.value(0)

def read_pulse_width():
    pulse_width = 0
    timeout = time.ticks_us() + 1000000  # 1 segundo de timeout
    while pin_echo.value() == 0:
        if time.ticks_us() > timeout:
            return 0
    pulse_start = time.ticks_us()
    while pin_echo.value() == 1:
        if time.ticks_us() > timeout:
            return 0
    pulse_end = time.ticks_us()
    pulse_duration = pulse_end - pulse_start
    return pulse_duration

def read_distance():
    trigger_pulse()
    pulse_width = read_pulse_width()
    distance = (pulse_width * 0.0343) / 2  # Convertir el tiempo a distancia en cm
    return distance

def publish_data(client, topic, value):
    if value > distance_limit:
        payload = "True"
        timestamp = time.localtime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        data = {
            "distance_exceeds_limit": payload,
            "timestamp": timestamp_str
        }
        client.publish(topic, json.dumps(data))
        print(f"Dato publicado en {topic}: {data}")

def display_distance(distance):
    oled.fill(0)
    oled.text("Distance: {:.2f} cm".format(distance), 0, 0)
    oled.show()

def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        distance = read_distance()
        display_distance(distance)
        publish_data(mqtt_client, mqtt_topic_distance, distance)
        time.sleep(3.5)

if __name__ == "__main__":
    main()
