FROM python:3.13-rc-slim as build

ARG device_model=mcintosh_mx160

ENV TEST=true \
    TEST2=true

WORKDIR /app

# install git and Python3 environment
RUN apk update \
 && apk add --no-cache bash git python3 jq \
 && python3 -m ensurepip \
 && rm -r /usr/lib/python*/ensurepip \
 && pip3 install --upgrade pip setuptools yq \
 && cd /usr/bin \
 && ln -sf pip3 pip \
 && ln -sf python3 python

COPY requirements.txt /app
RUN pip install -r requirements.txt

RUN git clone https://github.com/rsnodgrass/avemu.git /app  \
 && pip3 install --no-cache-dir -r "/app/requirements.txt" \
 && rm -rf /root/.cache /var/cache

#COPY . /app

EXPOSE 4999

CMD [ "./avemu", "--model", $device_model ]
