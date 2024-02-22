FROM python:3.13-rc-slim as build

ARG device_model=mcintosh_mx160

# install git
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && apt-get purge -y --auto-remove \
 && rm -rf /var/lib/apt/lists/*

# update Python
RUN pip install --upgrade pip

WORKDIR /app

RUN git clone https://github.com/rsnodgrass/avemu.git /app  \
 && pip3 install --no-cache-dir -r "/app/requirements.txt" \
 && rm -rf /root/.cache /var/cache


EXPOSE 4999

CMD [ "./avemu", "--model", $device_model ]
