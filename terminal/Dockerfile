FROM python:alpine

RUN mkdir /app
COPY terminal /app/terminal
COPY common /app/common
COPY requirements.txt /app

COPY proto/services/registration /app/proto/services/registration
COPY proto/services/terminal /app/proto/services/terminal

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    if [ -f terminal/requirements.txt ]; then \
        pip install -r terminal/requirements.txt; \
    fi

RUN python -m grpc_tools.protoc -I./ --python_out=. \
    --grpc_python_out=. --pyi_out=. \
    ./proto/services/registration/registration_service.proto \
    ./proto/services/terminal/terminal_service.proto

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENTRYPOINT ["python", "terminal/main.py"]
