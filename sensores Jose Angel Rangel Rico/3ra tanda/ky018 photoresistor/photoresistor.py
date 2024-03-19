from umqtt.simple import MQTTClient
from machine import Pin, ADC, SoftI2C
import time
import ssd1306
import json

# Configuración de la red WiFi
ssid = "Angel"
password = "12345678"

# Configuración del broker MQTT
mqtt_broker = "192.168.43.27"
mqtt_topic_light = "utng/arg/sound"

# Configuración del pin del sensor KY-018 Photoresistor (conectado al pin analógico ADC0)
pin_photoresistor = ADC(Pin(33))

# Límite de intensidad de luz
light_limit = 755  # Ejemplo: si la intensidad de luz supera 800, se enviará "True" al broker MQTT

# Configuración del display OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Configuración del cliente MQTT
mqtt_client = None

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
    global mqtt_client
    mqtt_client = MQTTClient("esp32", mqtt_broker)
    mqtt_client.connect()
    print("Conexión MQTT exitosa")

def read_light_sensor():
    # Leer el valor analógico del sensor de fotocélula
    return pin_photoresistor.read()

def publish_data(topic, value):
    global mqtt_client
    if mqtt_client is not None:
        if value < light_limit:
            payload = "True"
            timestamp = time.localtime()
            timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
            data = {
                "light_exceeds_limit": payload,
                "timestamp": timestamp_str
            }
            mqtt_client.publish(topic, json.dumps(data))
            print(f"Dato publicado en {topic}: {data}")

def display_light(intensity):
    oled.fill(0)
    oled.text("Intensity: {}".format(intensity), 0, 0)
    oled.show()

def main():
    connect_wifi()
    connect_mqtt()

    while True:
        intensity = read_light_sensor()
        display_light(intensity)
        publish_data(mqtt_topic_light, intensity)
        time.sleep(3.0)

if __name__ == "__main__":
    main()
