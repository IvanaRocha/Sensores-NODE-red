from umqtt.simple import MQTTClient
from machine import Pin, SoftI2C, ADC
import time
import ssd1306
import json

# Configuración de la red WiFi
ssid = "Angel"
password = "12345678"

# Configuración del broker MQTT
mqtt_broker = "192.168.43.27"
mqtt_topic_visible = "utng/arg/sound"
mqtt_topic_infrared = "utng/arg/sound"

# Configuración de los pines del sensor KY-027 2PCS Light Cup
pin_visible = ADC(Pin(35))  # Pin analógico para el sensor de luz visible
pin_infrared = ADC(Pin(34))  # Pin analógico para el sensor de luz infrarroja

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

def read_light_sensor(pin):
    return pin.read()

def publish_data(client, topic, value):
    if value > 500:  # Se considera inclinado si el valor del sensor es mayor que 500 (ajustar según necesidad)
        timestamp = time.localtime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        data = {
            "value": True,
            "timestamp": timestamp_str
        }
        client.publish(topic, json.dumps(data))
        print(f"Dato publicado en {topic}: {data}")


def display_values(visible_value, infrared_value):
    oled.fill(0)
    oled.text("Visible: {}".format(visible_value), 0, 0)
    oled.text("Infrared: {}".format(infrared_value), 0, 20)
    oled.show()

def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        visible_light = read_light_sensor(pin_visible)
        infrared_light = read_light_sensor(pin_infrared)
        
        display_values(visible_light, infrared_light)
        
        publish_data(mqtt_client, mqtt_topic_visible, visible_light)
        publish_data(mqtt_client, mqtt_topic_infrared, infrared_light)
        
        time.sleep(3.5)

if __name__ == "__main__":
    main()
