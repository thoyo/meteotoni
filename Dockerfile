FROM python:3.8

ENV METEOTONI /opt/meteotoni

RUN mkdir -p $METEOTONI
WORKDIR $METEOTONI

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

RUN apt update && apt-get -y install ffmpeg

# Only copy the code files
COPY main.py .
COPY .env .

CMD ["python", "-u", "main.py"]

