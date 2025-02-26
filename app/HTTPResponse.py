from typing import Dict, Optional, Type

# Класс для парсинга HTTP-ответа
class HTTPResponse:
    def __init__(self, status_code: int, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body or b""

    def to_bytes(self) -> bytes:
        status_line = f"HTTP/1.1 {self.status_code} OK\r\n"
        headers = "\r\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        return (status_line + headers + "\r\n\r\n").encode() + self.body

    @classmethod
    def from_bytes(cls: Type['HTTPResponse'], binary_data: bytes) -> 'HTTPResponse':
        lines = binary_data.split(b"\r\n")
        status_line = lines[0].decode().split()
        status_code = int(status_line[1])
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

        return cls(status_code, headers, body)
