FROM python:3.10.11

RUN apt-get update && \
    apt-get install -y supervisor && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/supervisor

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade prefect
RUN mkdir data

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY scripts/** /usr/src/app/scripts/

CMD ["/usr/src/app/scripts/entrypoint_script.sh"]
