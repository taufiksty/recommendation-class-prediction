FROM python:3.10.12-slim-bullseye

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "grpc_server.py" ]