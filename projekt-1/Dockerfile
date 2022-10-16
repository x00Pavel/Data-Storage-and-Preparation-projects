FROM ubuntu:latest

WORKDIR /app
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt setup.py /app/
COPY upaproject /app/upaproject
RUN pip3 install -e /app

ENTRYPOINT ["tail", "-f", "/dev/null"]
