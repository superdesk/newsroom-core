FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-venv git gcc curl pkg-config \
# lxml
libxml2-dev libxslt-dev \
# PIL
libjpeg-dev zlib1g-dev \
# magic
libmagic-dev \
# xmlsec
pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
&& rm -rf /var/lib/apt/lists/* 

# setup venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV C_FORCE_ROOT=False
ENV TZ=Europe/Prague

# update venv
RUN python3 -m pip install -U pip wheel setuptools

# install requirements
WORKDIR /opt/newsroom/
COPY requirements.txt .
RUN python3 -m pip install -Ur requirements.txt

# install newsroom app
COPY . .
RUN python3 -m pip install -e .

# setup entrypoint
WORKDIR /opt/newsroom/e2e/server/
ENTRYPOINT ["sh", "/opt/newsroom/e2e/server/scripts/start.sh"]
CMD ["honcho", "start", "-p 5050"]
