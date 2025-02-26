from app.HTTPRequest import HTTPRequest

def test_http_request_to_bytes():
    request = HTTPRequest(
        method="POST",
        path="/send_sms",
        host="localhost",
        headers={"Content-Type": "application/json"},
        body='{"message": "123"}'.encode('utf-8')
    )
    request_bytes = request.to_bytes()
    assert b"POST /send_sms HTTP/1.1" in request_bytes
    assert b"Content-Type: application/json" in request_bytes
    assert '{"message": "123"}'.encode('utf-8') in request_bytes

def test_http_request_from_bytes():
    raw_request = (
        b"POST /send_sms HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Content-Type: application/json\r\n"
        b"\r\n"
        b'{"message": "123"}'
    )
    request = HTTPRequest.from_bytes(raw_request)
    assert request.method == "POST"
    assert request.path == "/send_sms"
    assert request.host == "localhost"
    assert request.headers["Content-Type"] == "application/json"
    assert request.body == '{"message": "123"}\r\n'.encode('utf-8')
