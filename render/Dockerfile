FROM linuxserver/blender AS render-service
MAINTAINER danilburzua@gmail.com

ADD . /home/render

WORKDIR /home/render
RUN apt update && apt install -y python3-pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3",  "./app/main.py"]