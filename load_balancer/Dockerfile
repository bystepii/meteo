FROM python:alpine

RUN mkdir /app
COPY load_balancer /app/load_balancer
COPY common /app/common
COPY requirements.txt /app

COPY proto/messages/meteo /app/proto/messages/meteo
COPY proto/services/meteo /app/proto/services/meteo
COPY proto/services/registration /app/proto/services/registration
COPY proto/services/processing /app/proto/services/processing

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

RUN python -m grpc_tools.protoc -I./ --python_out=. \
    --grpc_python_out=. --pyi_out=. \
    ./proto/messages/meteo/meteo_messages.proto \
    ./proto/services/meteo/meteo_service.proto \
    ./proto/services/registration/registration_service.proto \
    ./proto/services/processing/processing_service.proto

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENTRYPOINT ["python", "load_balancer/main.py"]
