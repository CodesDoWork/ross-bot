FROM python:3.11-alpine

WORKDIR /app

RUN apk upgrade
RUN apk add --no-cache ffmpeg

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY res res
COPY src src

ENTRYPOINT ["python", "-m", "src.main"]
