FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN echo "[FreeTDS]\n\
Description=FreeTDS Driver\n\
Driver=/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup=/usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" > /etc/odbcinst.ini

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "marts.main"]
