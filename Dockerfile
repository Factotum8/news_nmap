FROM ubuntu

COPY ./setup.py ./setup.py

RUN apt-get update  -y && \
    apt-get install -y \
    python3.8-dev && \
apt-get install -y \
    python3-pip && \
pip3 install --no-cache-dir -e .

WORKDIR /opt/news_nmap/

COPY news_nmap/ news_nmap/
COPY mypackages/ mypackages/
COPY .env.yaml.default .env

CMD python3 ./news_nmap/news_nmap.py -p ./.env
