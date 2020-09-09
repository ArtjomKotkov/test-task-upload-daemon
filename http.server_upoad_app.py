#!/usr/bin/env python
import os
import hashlib as hl
import re
import mimetypes
from requests_toolbelt import MultipartDecoder
from http.server import HTTPServer, BaseHTTPRequestHandler

import daemon


class Handler(BaseHTTPRequestHandler):

    @property
    def hash(self):
        return self.path[1:]

    def _store_folder_existing(self, hash, force_create: bool = False):
        """Проверяет наличие папок store, и store/hash.

        Возвращает True или False в щависимос он наличия, и путь до папки или None.

        Parameters
        ---------
        force_create: bool
            Если указан как True, опускает проверки и создает папки store и store/hash.
        """
        if not os.path.isdir('store'):
            os.mkdir('store')
            if not force_create:
                return False, None
        folder_name = hash[:2]
        if force_create:
            try:
                os.mkdir(f'store/{folder_name}')
                return True, f'store/{folder_name}'
            except FileExistsError:
                return True, f'store/{folder_name}'
        return False, None if not os.path.isdir(f'store/{folder_name}') else True, f'store/{folder_name}'

    def _make_reasponse(self, status_code: int, headers: dict = None, message: str = None):
        if not headers:
            headers = {}
        self.send_response(code=status_code)
        for header in headers.items():
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(f'{message}\n'.encode())

    def _save_file(self, file, filename):
        hash = hl.md5(filename.encode()).hexdigest()
        filename, extension = os.path.splitext(filename)
        status, folder_path = self._store_folder_existing(hash=hash, force_create=True)
        with open(folder_path + f'/{hash}{extension}', 'wb') as local_file:
            local_file.write(file)
        return filename + extension, hash

    def _get_file(self, hash):
        """Return file path with name hash.(ext) or None and count of files in folder."""
        folder_path = os.path.join('store', hash[:2])
        if not os.path.isdir(folder_path):
            return None, None
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if re.match(rf'{hash}\..*', file) and 'x' in file or file == hash and not '.' in file:
                    file_path = os.path.join(root, file)
                    return file_path, len(files)
                return None, None

    def do_GET(self):
        if self.path == '/':
            return self._make_reasponse(400)
        file_hash = self.path[1:]
        file_path, count_of_files = self._get_file(file_hash)
        if file_path:
            with open(file_path, 'rb') as local_file:
                filename, ext = os.path.splitext(file_path)
                headers = {
                    'Content-Disposition': 'attachment; ' + f'filename="{file_hash+ext}"',
                    'content-type': mimetypes.guess_type(file_path)[0]
                }
                self._make_reasponse(200, headers=headers)
                self.wfile.write(local_file.read())
        else:
            self._make_reasponse(404, message=f'File {file_hash} not found.')

    def do_POST(self):
        if not self.headers['content-length']:
            self._make_reasponse(400, message='You must provide files for transfer.')
            return
        file = self.rfile.read(int(self.headers['content-length']))
        file_hashes = []
        if 'multipart/form-data' in self.headers['content-type']:
            data = MultipartDecoder(file, content_type=self.headers['content-type'])
            for part in data.parts:
                pattern_matches = re.findall(r'.*filename="(.*)".*',
                                             part.headers['Content-Disposition'.encode()].decode('utf-8'))
                if part.headers.get('Content-Type'.encode()) == 'application/octet-stream'.encode():
                    file_hashes.append(self._save_file(file=part.content, filename=pattern_matches[0]))
        else:
            self._make_reasponse(400, message='Для передачи файлов используйте content-type="multipart/form-data".')
        self._make_reasponse(200, message='\n'.join(map(lambda x: str(x), file_hashes)))

    def do_DELETE(self):
        file_hash = self.path[1:]
        file_path, count_of_files = self._get_file(file_hash)
        if file_path:
            os.remove(file_path)
            if count_of_files == 1:
                os.rmdir(f'store/{file_hash[:2]}')
                self._make_reasponse(200, message='OK')
        else:
            self._make_reasponse(404, message=f'File {file_hash} not found.')

#python http.server_upoad_app.py

if __name__ == '__main__':
    server_address = ('', 5000)
    http_server = HTTPServer(server_address, Handler)
    with daemon.DaemonContext():
        http_server.serve_forever()
