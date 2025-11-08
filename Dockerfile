FROM python:3.10-slim
WORKDIR /app
COPY requirements_docker.txt .

RUN apt-get update && \
    apt-get install -y gcc build-essential python3-dev && \
    pip install -r requirements_docker.txt && \
    apt-get purge -y gcc build-essential python3-dev && \
    apt-get autoremove -y && \
    apt-get clean


COPY . .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "main.py"]