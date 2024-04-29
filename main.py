import mimetypes 
import urllib.parse
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import socket
from threading import Thread
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = 'localhost'
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000


#jinja = Environment(loader=FileSystemLoader('templates'))


class GoItFramework(BaseHTTPRequestHandler):


    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        print(route.query)
        if route.path == "/":
            self.send_html("index.html")
        elif route.path == "/message":
            self.send_html("message.html")
   #     elif route.path == "/contact":
      #      self.send_html("contact.html")
        else:
            file = BASE_DIR.joinpath(route.path[1:])
            if file.exists():
                self.send_static(file)
            else:
                self.send_html("error.html", 404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

        

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


    # def render_template(self, filename, status_code=200):
    #     self.send_response(status_code)
    #     self.send_header('Content-Type', 'text/html')
    #     self.end_headers()
    #
    #     with open('storage/db.json', 'r', encoding= 'utf-8') as file:
    #         data = json.load(file)
    #
    #     template = jinja.get_template(filename)
    #     html = template.render(blogs=data)
    #     self.wfile.write(html.encode())
        
    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_data = {current_time: {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}

        file_path = "data.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}
        except ValueError:
            existing_data = {}

        existing_data.update(new_data)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=2)

    except ValueError as error:
        logging.error(f"ValueError: {error}")
    except OSError as oser:
        logging.error(f"OSError: {oser}")

def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, GoItFramework)
    logging.info('Starting http server')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()

def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info("Starting socket")
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info("++")
            save_data(msg)
    except KeyboardInterrupt:
        server_socket.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(threadName)s] %(message)s', level=logging.INFO)
    logging.info('Starting socket server')

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()