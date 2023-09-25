FROM python:3.11
ENV PYTHONUNBUFFERED 1

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./service/requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt

COPY ./service/ /src/

CMD [ "flask", "--app", "app", "run","--host","0.0.0.0","--port","5000"]