FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
WORKDIR /code
COPY addressbook/ /code/
COPY contacts/ /code/
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/