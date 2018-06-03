FROM amazonlinux:latest

RUN yum install python35 python35-devel python35-pip python35-setuptools python35-virtualenv -y
RUN pip-3.5 install --upgrade pip
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

ADD web.py web.py