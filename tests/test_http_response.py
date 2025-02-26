from app.HTTPResponse import HTTPResponse

def test_http_response_to_bytes():
    response = HTTPResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body=b'{"status": "success"}'
    )
    response_bytes = response.to_bytes()
    assert b"HTTP/1.1 200 OK" in response_bytes
    assert b"Content-Type: application/json" in response_bytes
    assert b'{"status": "success"}' in response_bytes

def test_http_response_from_bytes():
    raw_response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"\r\n"
        b'{"status": "success"}'
    )
    response = HTTPResponse.from_bytes(raw_response)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == b'{"status": "success"}\r\n'
