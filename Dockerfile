FROM python:3.6.7

RUN adduser --home /home/nju_dc --shell /bin/bash --disabled-password nju_dc

WORKDIR /home/nju_dc

ADD docker/apt/sources.list /etc/apt/

RUN apt-get update -y
RUN apt-get install -y mysql-client
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple gunicorn

COPY app app
COPY instance instance
COPY migrations migrations
COPY docker docker
RUN chmod +x docker/boot.sh

ENV FLASK_APP=app

RUN mkdir -p /var/log/flask && chown -R nju_dc:nju_dc /var/log/flask
RUN mkdir -p /var/log/gunicorn && chown -R nju_dc:nju_dc /var/log/gunicorn
RUN chown -R nju_dc:nju_dc ./

USER nju_dc

EXPOSE 5000
ENTRYPOINT ["./docker/boot.sh"]
