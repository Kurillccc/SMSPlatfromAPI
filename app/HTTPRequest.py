from typing import Dict, Optional, Type

# Класс для формирования и парсинга HTTP-запроса
class HTTPRequest:
    def __init__(self, method: str, path: str, host: str, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None):
        self.method = method
        self.path = path
        self.host = host
        self.headers = headers or {}
        self.body = body or b""

    def to_bytes(self) -> bytes:
        request_line = f"{self.method} {self.path} HTTP/1.1\r\n"
        headers = "\r\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        return (request_line + headers + "\r\n\r\n").encode() + self.body

    @classmethod
    def from_bytes(cls: Type['HTTPRequest'], binary_data: bytes) -> 'HTTPRequest':
        lines = binary_data.split(b"\r\n")
        request_line = lines[0].decode().split()
        method, path = request_line[0], request_line[1]
        host = ""
        headers = {}
        body = b""

        is_body = False
        for line in lines[1:]:
            if line == b"":
                is_body = True
                continue
            if is_body:
                body += line + b"\r\n"
            else:
                key, value = line.decode().split(":", 1)
                headers[key.strip()] = value.strip()
                if key.lower() == "host":
                    host = value.strip()

        return cls(method, path, host, headers, body)
