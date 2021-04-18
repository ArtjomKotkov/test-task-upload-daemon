# *Nix Python file storage daemons 

Демон для хранения файлов представлен в двух вариантах, как WSGI (Flask) приложение, 
второй вариант представляет из себя http.server из стандартной библиотеки, 
оба варианта поддерживают download (GET), upload (POST), delete (DELETE). 
Загрузку можно производить сразу по несколько файлов.

# Installation 

```bash
$ pipenv sheell
$ pip install -r [flask or http.server]_requirements.txt
```

# Запуск

Flask приложение запускается с использованием gunicorn.
```bash
$ gunicorn -D flask_upload_app:app
```

Запуск Http сервера осуществляется как обычный запуск python скрипта.
```bash
$ python3 http.server_upload_app.py
```
