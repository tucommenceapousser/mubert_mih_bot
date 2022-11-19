# from pytorch/pytorch:latest 
from python:3.10

    label mantainer cucumberian

    run mkdir -p /usr/src/app/

    copy ./app.py ./utils.py ./constants.py ./requirements.txt ./mubert.py  /usr/src/app/

    workdir /usr/src/app/

    # install requirements
    run pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

    # download dependencies
    run python3 /usr/src/app/mubert.py


    cmd ["python3", "app.py"]

    

