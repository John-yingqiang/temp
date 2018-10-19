FROM python:3.6
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple --no-cache-dir -r requirements.txt
COPY . /usr/src/app
RUN useradd -s /usr/sbin/nologin someone