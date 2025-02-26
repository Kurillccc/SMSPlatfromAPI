import asyncio
import tomli
import argparse
import base64
import json
import asyncio.streams

from pathlib import Path
from app.HTTPRequest import HTTPRequest
from app.HTTPResponse import HTTPResponse
from typing import Dict

CONFIG_PATH = 'app/config.toml'

def load_config(file_path: str) -> Dict[str, str]:
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Config file '{file_path}' not found.")

    with open(file_path, 'rb') as f:
        config = tomli.load(f)

    required_keys = ['service_url', 'username', 'password']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    return config

parser = argparse.ArgumentParser(description='Отправка СМС')
parser.add_argument('--sender', required=True, help='Номер отправителя')
parser.add_argument('--recipient', required=True, help='Номер получателя')
parser.add_argument('--message', required=True, help='Текст сообщения')
args = parser.parse_args()

async def send_sms(config: Dict[str, str], sender: str, recipient: str, message: str) -> None:
    url = config['service_url'].replace('http://', '')
    host, port = url.split(':')
    port = int(port) if port else 80
    auth = base64.b64encode(f"{config['username']}:{config['password']}".encode()).decode()
    payload = json.dumps({
        "sender": sender,
        "recipient": recipient,
        "message": message
    }).encode()

    headers = {
        "Host": host,
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Content-Length": str(len(payload)),
        "Connection": "close"
    }

    # Формируем запрос с HTTPRequest
    request = HTTPRequest("POST", "/send_sms", host, headers, payload)
    request_bytes = request.to_bytes()

    reader, writer = await asyncio.open_connection(host, port)
    writer.write(request_bytes)
    await writer.drain()

    response_data = await reader.read()
    print("\nОтвет сервера (в виде байтов):")
    print(response_data)

    # Парсим ответ с HTTPResponse
    response = HTTPResponse.from_bytes(response_data)
    if response.status_code == 200:
        print("\nОтвет сервера (парсинг):")
        print("Код ответа:", response.status_code)
        print("Тело ответа:", response.body.decode())
        print("Заголовки:", response.headers)
    elif response.status_code == 400:
        print("Код ответа:", response.status_code)
        print("Invalid parameters")
    elif response.status_code == 401:
        print("Код ответа:", response.status_code)
        print("Invalid credentials")
    elif response.status_code == 500:
        print("Код ответа:", response.status_code)
        print("Internal server error")

    writer.close()
    await writer.wait_closed()

async def main() -> None:
    config = load_config(CONFIG_PATH)
    await send_sms(config, args.sender, args.recipient, args.message)

if __name__ == '__main__':
    asyncio.run(main())