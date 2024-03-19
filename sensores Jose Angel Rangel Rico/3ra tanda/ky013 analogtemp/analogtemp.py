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
mqtt_topic_temp = "utng/arg/sound"

# Configuración del pin del sensor KY-013 Analog Temp (conectado al pin analógico ADC0)
pin_temp = ADC(Pin(33))

# Límite de temperatura en grados Celsius
temperature_limit = 30.0  # Ejemplo: si la temperatura supera los 30 grados Celsius, se enviará "True"

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

def read_temp_sensor():
    # Leer el valor analógico del sensor de temperatura
    # Convertir el valor a temperatura en grados Celsius
    # (El valor de conversión puede variar según las características del sensor)
    return (pin_temp.read() / 4095) * 100  # Suponiendo que el sensor es lineal en el rango de 0 a 100 grados Celsius

def publish_data(client, topic, value):
    if value > temperature_limit:
        payload = "True"
        timestamp = time.localtime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        data = {
            "temperature_exceeds_limit": payload,
            "timestamp": timestamp_str
        }
        client.publish(topic, json.dumps(data))
        print(f"Dato publicado en {topic}: {data}")

def display_temperature(temperature):
    oled.fill(0)
    oled.text("Temperature: {:.2f} C".format(temperature), 0, 0)
    oled.show()

def main():
    connect_wifi()
    mqtt_client = connect_mqtt()

    while True:
        temperature = read_temp_sensor()
        display_temperature(temperature)
        publish_data(mqtt_client, mqtt_topic_temp, temperature)
        time.sleep(3.5)

if __name__ == "__main__":
    main()
