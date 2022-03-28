FROM python:3

ENV TZ="Asia/Bangkok"

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y httpie
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/sh","-c", "python ./app.py"]
