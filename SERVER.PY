import http.server
import socketserver
import json
import os
import sys
import webbrowser
import base64
import platform
import subprocess
import zipfile
from datetime import datetime

# Prevent crashes in PyInstaller --windowed mode where sys.stdout/stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# Set working directory to the directory where the .exe or script is located
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)

# Ensure working directories exist
os.makedirs('quotes', exist_ok=True)
os.makedirs('QuotePDFs', exist_ok=True)
os.makedirs('images', exist_ok=True)
os.makedirs('Backups', exist_ok=True)

PORT = 8000

class LocalDiskHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'

        if self.path == '/api/load':
            data = {
                'presets': self.read_json('presets.json', []),
                'terms': self.read_json('terms.json', []),
                'clients': self.read_json('clients.json', []),
                'images': self.read_json('images.json', []),
                'quotes': self.load_all_quotes()
            }
            self.send_json_response(data)
        else:
            if self.path == '/index.html' and not os.path.exists('index.html'):
                if hasattr(sys, '_MEIPASS'):
                    bundled_index = os.path.join(sys._MEIPASS, 'index.html')
                    if os.path.exists(bundled_index):
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.end_headers()
                        with open(bundled_index, 'rb') as f:
                            self.wfile.write(f.read())
                        return
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        req = json.loads(body.decode('utf-8')) if body else {}

        if self.path == '/api/save_config':
            if 'presets' in req: self.write_json('presets.json', req['presets'])
            if 'terms' in req: self.write_json('terms.json', req['terms'])
            if 'clients' in req: self.write_json('clients.json', req['clients'])
            if 'images' in req: self.write_json('images.json', req['images'])
            self.send_json_response({'status': 'ok'})

        elif self.path == '/api/save_quote':
            filename = req.get('fileName')
            quote_data = req.get('data')
            if filename and quote_data:
                filepath = os.path.join('quotes', filename)
                self.write_json(filepath, quote_data)
            self.send_json_response({'status': 'ok'})

        elif self.path == '/api/save_pdf':
            filename = req.get('fileName')
            pdf_data = req.get('pdfData', '')
            if filename and pdf_data:
                if ',' in pdf_data:
                    pdf_data = pdf_data.split(',')[1]
                filepath = os.path.join('QuotePDFs', filename)
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(pdf_data))
            self.send_json_response({'status': 'ok'})

        elif self.path == '/api/delete_quote':
            filename = req.get('fileName')
            if filename:
                filepath = os.path.join('quotes', filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            self.send_json_response({'status': 'ok'})

        elif self.path == '/api/open_pdf_folder':
            pdf_dir = os.path.join(BASE_DIR, 'QuotePDFs')
            os.makedirs(pdf_dir, exist_ok=True)
            system_os = platform.system()
            if system_os == 'Windows':
                os.startfile(pdf_dir)
            elif system_os == 'Darwin':
                subprocess.run(['open', pdf_dir])
            else:
                subprocess.run(['xdg-open', pdf_dir])
            self.send_json_response({'status': 'ok'})

        elif self.path == '/api/create_backup':
            backup_dir = os.path.join(BASE_DIR, 'Backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            zip_filename = f"Petrie_Backup_{timestamp}.zip"
            zip_path = os.path.join(backup_dir, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for json_file in ['presets.json', 'terms.json', 'clients.json', 'images.json']:
                    if os.path.exists(json_file):
                        zipf.write(json_file, json_file)
                for folder in ['quotes', 'QuotePDFs', 'images']:
                    if os.path.exists(folder):
                        for root, dirs, files in os.walk(folder):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, BASE_DIR)
                                zipf.write(file_path, arcname)

            system_os = platform.system()
            if system_os == 'Windows':
                os.startfile(backup_dir)
            elif system_os == 'Darwin':
                subprocess.run(['open', backup_dir])

            self.send_json_response({'status': 'ok', 'filename': zip_filename})

        elif self.path == '/api/restore_backup':
            zip_b64 = req.get('zipData', '')
            if zip_b64:
                if ',' in zip_b64:
                    zip_b64 = zip_b64.split(',')[1]
                zip_bytes = base64.b64decode(zip_b64)
                temp_zip = os.path.join(BASE_DIR, 'temp_restore.zip')
                with open(temp_zip, 'wb') as f:
                    f.write(zip_bytes)
                with zipfile.ZipFile(temp_zip, 'r') as zipf:
                    zipf.extractall(BASE_DIR)
                if os.path.exists(temp_zip):
                    os.remove(temp_zip)
                self.send_json_response({'status': 'ok'})
            else:
                self.send_json_response({'status': 'error'})

        else:
            self.send_error(404, "Endpoint not found")

    def read_json(self, filename, default):
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def write_json(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_all_quotes(self):
        quotes = {}
        if os.path.exists('quotes'):
            for f in os.listdir('quotes'):
                if f.endswith('.json'):
                    content = self.read_json(os.path.join('quotes', f), None)
                    if content:
                        quotes[f] = content
        return quotes

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

socketserver.TCPServer.allow_reuse_address = True

while True:
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), LocalDiskHandler) as httpd:
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            httpd.serve_forever()
        break
    except OSError as e:
        if getattr(e, 'winerror', None) in (10048, 10013) or e.errno in (98, 13):
            PORT += 1
        else:
            raise e