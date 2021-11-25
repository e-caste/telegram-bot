FROM python:3.6-slim-buster

# set container timezone to Europe/Rome
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*
RUN ln -fs /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p /bot/{data,logs,pics}
WORKDIR /bot
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

ENV LOG_PATH="/bot/logs/"
ENV PICS_DIR="/bot/pics/"

COPY *.py ./

CMD ["python", "-u", "telegram_pi_bot.py"]

# build with
#   docker build -t pibot .
# run with
# -e TOKEN=... -e CST_CID=...