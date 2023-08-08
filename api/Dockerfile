FROM python

ADD . /home/api

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /home/api
RUN apt update && apt install -y python3-pip
RUN pip install -r requirements.txt
EXPOSE 5000

ENTRYPOINT ["flask",  "run"]