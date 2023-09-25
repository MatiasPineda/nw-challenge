FROM python:3.11.5

ENV PYTHONUNBUFFERED 1

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /src/requirements.txt
RUN pip install -r requirements.txt

COPY . /src/

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]