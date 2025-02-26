import argparse
import asyncio
import asyncio.streams
import base64
import json
import logging
from pathlib import Path
from typing import Dict

import tomli

from app.HTTPRequest import HTTPRequest
from app.HTTPResponse import HTTPResponse

CONFIG_PATH = 'app/config.toml'

logging.basicConfig(
    filename='app/sms_sender.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(file_path: str) -> Dict[str, str]:
    if not Path(file_path).is_file():
        logging.error(f"Config file '{file_path}' not found.")
        raise FileNotFoundError(f"Config file '{file_path}' not found.")

    with open(file_path, 'rb') as f:
        config = tomli.load(f)

    required_keys = ['service_url', 'username', 'password']
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required config key: {key}")
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

    logging.info(f"Отправка запроса на: http://{host}:{port}/send_sms")
    logging.info(f"Отправляемые данные: {json.dumps({'sender': sender, 'recipient': recipient, 'message': message}, ensure_ascii=False)}")

    # Формируем запрос с HTTPRequest
    request = HTTPRequest("POST", "/send_sms", host, headers, payload)
    request_bytes = request.to_bytes()

    logging.info("Отправка запроса на сервер...")
    logging.debug(f"Запрос: {request_bytes.decode()}")

    reader, writer = await asyncio.open_connection(host, port)
    writer.write(request_bytes)
    await writer.drain()

    response_data = await reader.read()

    logging.info("Получен ответ от сервера.")
    logging.debug(f"Ответ (в виде байтов): {response_data}")
    print("\nОтвет сервера (в виде байтов):")
    print(response_data)

    # Парсим ответ с HTTPResponse
    response = HTTPResponse.from_bytes(response_data)

    if response.status_code == 200:
        logging.info("Сообщение успешно отправлено.")
        logging.info(f"Код ответа от сервера: {response.status_code}")
        logging.info(f"Тело ответа: {response.body.decode()}")
        logging.debug(f"Ответ (парсинг): {response.body.decode()}")
        print("\nОтвет сервера (парсинг):")
        print("Код ответа:", response.status_code)
        print("Тело ответа:", response.body.decode())
        print("Заголовки:", response.headers)
    elif response.status_code == 400:
        logging.error("Некорректный запрос. Код ответа: 400")
        print("Код ответа:", response.status_code)
        print("Invalid parameters")
    elif response.status_code == 401:
        logging.error("Ошибка авторизации. Код ответа: 401")
        print("Код ответа:", response.status_code)
        print("Invalid credentials")
    elif response.status_code == 500:
        logging.error("Внутренняя ошибка сервера. Код ответа: 500")
        print("Код ответа:", response.status_code)
        print("Internal server error")

    writer.close()
    await writer.wait_closed()

async def main() -> None:
    try:
        config = load_config(CONFIG_PATH)
        await send_sms(config, args.sender, args.recipient, args.message)
    except Exception as e:
        logging.exception("Произошла ошибка в процессе отправки СМС.")

if __name__ == '__main__':
    asyncio.run(main())