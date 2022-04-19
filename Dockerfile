FROM python:3.10-alpine

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