FROM python:3

WORKDIR /usr/src/coderr-backend

COPY requirements.txt ./
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Port für Django öffnen
EXPOSE 8000

# Startskript festlegen
CMD ["sh", "entrypoint.sh"]
