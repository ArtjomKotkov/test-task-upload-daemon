import os
import re

from flask import Flask, request, Response, send_file
from flask.views import MethodView

import hashlib as hl

app = Flask(__name__)


# python flask_upload_app.py

class UploadApi(MethodView):
    def get(self, hash):
        folder_name = hash[:2]
        if not os.path.isdir(f'store/{folder_name}'):
            return Response(status=404, content_type='text/plain', response='File doesn\'t exist')
        for root, dirs, files in os.walk(f'store/{folder_name}'):
            for file in files:
                if re.search(rf'{hash}.*', file) is not None:
                    file_path = os.path.join(root, file)
                    return send_file(file_path)
                return Response(status=404, content_type='text/plain', response='File doesn\'t exist')

    def post(self, hash=None):
        print(request.files)
        if not request.files:
            return 'Request body must contains file.', 400
        files_hash = []
        for file in request.files.values():

            hash_str = hl.md5(file.filename.encode()).hexdigest()
            filename, file_extension = os.path.splitext(file.filename)
            new_name = hash_str + file_extension
            if not os.path.isdir('store'):
                os.mkdir('store')
            try:
                os.mkdir(path=f'store/{hash_str[:2]}')
            except FileExistsError:
                pass
            file.save(os.path.join('store', hash_str[:2], new_name))
            files_hash.append((file.filename, hash_str))

        return Response(status=201, content_type='text/plain',
                        response='\n'.join(map(lambda x: str(x), files_hash)) + '\n')

    def delete(self, hash):
        folder_name = hash[:2]
        if not os.path.isdir(f'store/{folder_name}'):
            return Response(status=404, content_type='text/plain', response='File doesn\'t exist')
        for root, dirs, files in os.walk(f'store/{folder_name}'):
            for file in files:
                if re.match(rf'{hash}\..*', file):
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    if len(files) == 1:
                        os.rmdir(f'store/{folder_name}')
                    return Response(status=200)
                return Response(status=404, content_type='text/plain', response='File doesn\'t exist')


app.add_url_rule(rule='/<hash>', view_func=UploadApi.as_view(name='upload_api'))
app.add_url_rule(rule='/', view_func=UploadApi.as_view(name='upload_api_2'))

if __name__ == '__main__':
    app.run(debug=True)
