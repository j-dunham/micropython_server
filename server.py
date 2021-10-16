import json
from socket import socket


class Request:
    def __init__(self, raw_request: list) -> None:
        method, raw_path, *_ = raw_request[0].split()
        path, *query_params = raw_path.split("?")
        self.method = method
        self.path = path
        self.query_params = query_params
        self.headers = self.parse_header(raw_request)

    def parse_header(self, request: list) -> dict:
        headers = {}
        for entry in request[1:-1]:
            key, value = entry.split(": ")
            headers[key] = value.replace("\r\n", "")
        return headers

    def __str__(self) -> str:
        return "%s:%s:%s" % (self.method, self.path, ",".join(self.query_params))


class SocketServer:
    def __init__(
        self,
        address: tuple,
        max_clients: int = 1,
        print_func=None,
    ) -> None:
        self._socket = socket()
        self.address = address
        self.max_clients = max_clients
        self.print = print_func or print

    def serve(self):
        self._socket.bind(self.address)
        self._socket.listen(self.max_clients)
        while True:
            client, addr = self._socket.accept()
            request = self.read_request(client)
            handler = self.resolve_path_handler(request.path)
            payload, code = handler(request)
            self.send_response(client, payload, code)
            self.close_connection(client)

    def default_handler(self, request) -> tuple:
        payload = {"status": "unknown"}
        self.print(request)
        return payload, 200

    def close_connection(self, client):
        client.close()

    def send_response(self, client, payload: dict, response_code: int = 200):
        header = "HTTP/1.0 {0}\r\nContent-type: text/json\r\n\r\n".format(response_code)
        client.send(header)
        response = json.dumps(payload)
        client.send(response)

    def read_request(self, client):
        cl_file = client.makefile("rwb", 0)
        lines = []
        while True:
            line = cl_file.readline()
            lines.append(line.decode())
            if not line or line == b"\r\n":
                break
        print(lines)
        return Request(lines)

    def resolve_path_handler(self, path: str):
        """Returns method matching path or default handler"""
        path = path[1:].replace("/", "_")
        handler = getattr(self, path, self.default_handler)
        return handler


class SecureServer(SocketServer):
    def __init__(self, auth_token, *args, **kwargs) -> None:
        self.auth_token = auth_token
        super().__init__(*args, **kwargs)

    def ping(self, request):
        """Test endpoint"""
        status = 404
        response = {"status": "pong"}
        self.print("Pong")
        if request.headers.get("Authorization") == self.auth_token:
            self.print("Authorized")
            status = 200
        self.print(request.headers)
        return response, status
