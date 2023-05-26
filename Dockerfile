FROM python:3.8

ENV METEOTONI /opt/meteotoni

RUN mkdir -p $METEOTONI

COPY requirements.txt $METEOTONI/requirements.txt
COPY main.py $METEOTONI/main.py
COPY .env $METEOTONI/.env

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

RUN apt update
RUN apt-get -y install ffmpeg
RUN pip install -r $METEOTONI/requirements.txt

WORKDIR $METEOTONI
# CMD ["python", "-u", "main.py", "new"]
CMD ["python", "-u", "main.py", "cache"]
