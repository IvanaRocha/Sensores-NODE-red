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

# Configuración de los pines del sensor de ultrasonido HC-SR04
pin_trigger = Pin(15, Pin.OUT)  # Pin de disparo (Trigger)
pin_echo = Pin(16, Pin.IN)      # Pin de eco (Echo)

# Configuración del pin del buzzer KY-012 (conectado al pin digital D5)
pin_buzzer = Pin(17, Pin.OUT)

# Límite de distancia en centímetros
distance_limit = 50  # Ejemplo: si la distancia es menor o igual a 50 cm, se enviará "True" al broker MQTT

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

def read_distance_sensor():
    # Generar un pulso de 10 microsegundos en el pin de disparo
    pin_trigger.value(1)
    time.sleep_us(10)
    pin_trigger.value(0)
    
    # Medir el tiempo de respuesta en el pin de eco
    pulse_time = time.ticks_us()
    while pin_echo.value() == 0:
        pulse_time = time.ticks_us()
    while pin_echo.value() == 1:
        echo_time = time.ticks_us()
        if time.ticks_diff(echo_time, pulse_time) > 50000:  # Espera máxima de 50 ms (equivalente a una distancia de 8.5 m)
            return -1
    # Calcular la duración del eco y convertirlo en distancia (en centímetros)
    pulse_duration = time.ticks_diff(echo_time, pulse_time)
    distance = pulse_duration * 0.0343 / 2
    return distance

def control_buzzer(distance):
    if distance <= distance_limit:
        pin_buzzer.on()  # Encender el buzzer si la distancia es menor o igual al límite
    else:
        pin_buzzer.off()  # Apagar el buzzer si la distancia es mayor al límite

def publish_data(topic, value):
    global mqtt_client
    if mqtt_client is not None:
        payload = "True" if value else "False"
        timestamp = time.localtime()
        timestamp_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])
        data = {
            "distance_exceeds_limit": payload,
            "timestamp": timestamp_str
        }
        mqtt_client.publish(topic, json.dumps(data))
        print(f"Dato publicado en {topic}: {data}")

def display_distance(distance):
    oled.fill(0)
    oled.text("Distance: {:.2f} cm".format(distance), 0, 0)
    oled.show()

def main():
    connect_wifi()
    connect_mqtt()

    while True:
        distance = read_distance_sensor()
        if distance != -1:
            control_buzzer(distance)
            display_distance(distance)
            publish_data(mqtt_topic_distance, distance)
        time.sleep(3.0)

if __name__ == "__main__":
    main()
