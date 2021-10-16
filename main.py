from socket import getaddrinfo
from utils import toggle_onboard_led, connect_to_wifi, read_config
from server import SecureServer


def run():
    config = read_config("config.json")
    toggle_onboard_led(5, 1)

    connect_to_wifi(config["ssid"], config["wifi_password"])
    addr = getaddrinfo("0.0.0.0", 80)[0][-1]
    server = SecureServer(address=addr, auth_token=config["auth_token"])
    server.serve()


if __name__ == "__main__":
    run()
