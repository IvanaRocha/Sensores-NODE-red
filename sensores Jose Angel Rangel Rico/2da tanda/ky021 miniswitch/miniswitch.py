#miniswitch

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
mqtt_topic = "utng/arg/sound"

# Configuración del pin del sensor KY-021 Mini Switch (conectado al pin digital D4)
pin_miniswitch = Pin(4, Pin.IN)

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

def read_miniswitch_sensor():
    return pin_miniswitch.value()

def publish_data(client, topic, payload):
    if payload:
        timestamp = time.localtime()  # Obtener la marca de tiempo actual como una tupla
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        data = {
            "switch_state": True,
            "timestamp": timestamp_str
        }
        client.publish(topic, json.dumps(data))  # Publicar los datos como un JSON
        print(f"Dato publicado en {topic}: {data}")

def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        switch_state = read_miniswitch_sensor()
        if switch_state:
            publish_data(mqtt_client, mqtt_topic, True)
            time.sleep(3.5)  # Espera antes de volver a verificar el sensor

if __name__ == "__main__":
    main()

