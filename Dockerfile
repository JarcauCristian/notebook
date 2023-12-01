FROM python:3.11-slim-bullseye

USER root

RUN addgroup nopermission && useradd noperm -m -s /bin/bash && adduser noperm nopermission

RUN mkdir /home/noperm/notebooks && \
    chown noperm:nopermission /home/noperm/notebooks && \
    chmod 700 /home/noperm/notebooks

COPY requirements.txt /home/noperm/
COPY save_to_postgres.py /home/noperm/
COPY upload_to_mlflow.py /home/noperm/

RUN chmod 111 /home/noperm/save_to_postgres.py
RUN chmod 111 /home/noperm/upload_to_mlflow.py

RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN chmod 555 /lib /lib64

RUN chmod 500 /boot /etc /media /mnt /opt /proc /run /sbin /srv /var

RUN pip install notebook
RUN pip install -r /home/noperm/requirements.txt

WORKDIR /home/noperm/notebooks

USER noperm

ENV NOTEBOOK_ID=null
ENV SERVICE_NAME=api-deleter-service
ENV SERVICE_PORT=49153
ENV DATASET_URL=null

COPY ./template.ipynb /home/noperm/notebooks/ModelCreation.ipynb

EXPOSE 8888

CMD ["sh", "-c", "jupyter notebook --notebook-dir=/home/noperm/notebooks --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.tornado_settings="{\"headers\":{\"Content-Security-Policy\":\"frame-ancestors 'self' https://equipped-woodcock-needlessly.ngrok-free.app\"}}" --NotebookApp.base_url=/${NOTEBOOK_ID} --NotebookApp.token=${JUPYTER_TOKEN} --NotebookApp.file_to_run=/home/noperm/notebooks/ModelCreation.ipynb"]
