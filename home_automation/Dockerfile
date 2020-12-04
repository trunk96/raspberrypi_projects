FROM debian:stable-slim
RUN apt-get update
RUN apt-get install -y python3 python3-pip build-essential libssl-dev libffi-dev python3-setuptools
RUN python3 -m pip install flask requests gunicorn zeroconf
RUN mkdir /app
WORKDIR /app
ADD . /app
CMD gunicorn --bind 0.0.0.0:80 --preload wsgi:app
