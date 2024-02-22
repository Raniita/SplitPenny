FROM python:3.11-slim-bullseye

RUN mkdir src
WORKDIR /src

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# for migrations
# COPY migrations .

COPY . .

EXPOSE 5000

# Default is not set or production
ENV FASTAPI_CONFIG=$FASTAPI_CONFIG  
CMD if [ "$FASTAPI_CONFIG" = "development" ] ; \
then uvicorn app.main:app --reload --host 0.0.0.0 --port 5000; \
else uvicorn app.main:app --host 0.0.0.0 --port 5000; \
fi