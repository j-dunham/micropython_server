import json
import network
from time import sleep
from machine import Pin


def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())


def read_config(config_path):
    with open(config_path, "r") as fout:
        config = json.load(fout)
    return config


def toggle_onboard_led(times, delay):
    led = Pin(2, Pin.OUT)
    for x in range(times):
        led.off() if led.value() else led.on()
        sleep(delay)
