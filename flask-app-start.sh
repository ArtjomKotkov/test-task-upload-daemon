#!/bin/bash

if [[ $VIRTUAL_ENV != "" ]]
then
  pip install -r flask_requirements.txt
  gunicron -D flask_upload_app:app
else
  pipenv shell
  pip install -r flask_requirements.txt
  gunicron -D flask_upload_app:app
fi

