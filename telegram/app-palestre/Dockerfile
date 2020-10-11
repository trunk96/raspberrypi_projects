FROM balenalib/rpi-raspbian:latest
RUN apt-get update
RUN apt-get install -y python3-pip
WORKDIR /app
ADD requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ADD bot.py /app/
ADD picklepersistencejobs.py /app/
ADD API_KEY.txt /app/
ENTRYPOINT ["python3", "bot.py"]

