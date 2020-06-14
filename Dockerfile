FROM ubuntu

COPY ./setup.py ./setup.py

RUN apt-get update  -y && \
    apt-get install -y \
    python3.8-dev && \
apt-get install -y \
    python3-pip && \
pip3 install --no-cache-dir -e . && \
apt-get remove -y python3.8-dev && \
apt-get autoremove -y && \
apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nmap

COPY news_nmap/ news_nmap/
COPY mypackages/ limypackages/
COPY .env.default .env

CMD /usr/bin/python3 ./news_nmap/news_nmap.py -p ./.env
