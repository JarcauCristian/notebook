FROM python:3.11-slim-bullseye

USER root

RUN addgroup nopermission && useradd noperm -m -s /bin/bash && adduser noperm nopermission

RUN mkdir /home/noperm/notebooks && \
    chown noperm:nopermission /home/noperm/notebooks && \
    chmod 764 /home/noperm/notebooks 

COPY classification.ipynb /home/noperm/notebooks/classification.ipynb
COPY regression.ipynb /home/noperm/notebooks/regression.ipynb
COPY clustering.ipynb /home/noperm/notebooks/clustering.ipynb
COPY metrics.py /home/noperm/notebooks/metrics.py
RUN chmod 776 /home/noperm/notebooks/classification.ipynb
RUN chmod 776 /home/noperm/notebooks/regression.ipynb
RUN chmod 776 /home/noperm/notebooks/clustering.ipynb
RUN chmod 555 /home/noperm/notebooks/metrics.py
COPY ./jupyter_notebook_config.py /home/noperm/csp_config.py

COPY requirements.txt /home/noperm/

RUN apt-get update && \
    apt-get install -y gcc libomp-dev cmake g++ git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN chmod 500 /boot /etc /media /mnt /opt /proc /run /sbin /srv /var

RUN pip install notebook
RUN pip install -r /home/noperm/requirements.txt

WORKDIR /home/noperm/notebooks

USER noperm

ENV NOTEBOOK_ID=null
ENV SERVICE_NAME=api-deleter-service
ENV SERVICE_PORT=49153
ENV DATASET_URL=null

EXPOSE 8888

CMD jupyter notebook --NotebookApp.base_url=/${NOTEBOOK_ID} --NotebookApp.token='' --NotebookApp.password='' --ip=0.0.0.0 --port=8888 --no-browser --config=/home/noperm/csp_config.py
