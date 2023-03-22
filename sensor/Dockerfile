FROM python:slim

RUN mkdir /app
COPY sensor /app/sensor
COPY common /app/common
COPY requirements.txt /app

COPY proto/messages/meteo /app/proto/messages/meteo
COPY proto/services/meteo /app/proto/services/meteo

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache \
      if [ -f sensor/requirements.txt ]; then \
        pip install -r sensor/requirements.txt; \
    fi

RUN python -m grpc_tools.protoc -I./ --python_out=. \
    --grpc_python_out=. --pyi_out=. \
    ./proto/messages/meteo/meteo_messages.proto \
    ./proto/services/meteo/meteo_service.proto

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENTRYPOINT ["python", "sensor/main.py"]
