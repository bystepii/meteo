# Distributed meteorological data processing system
## Implementation 1: direct communication

This is the first implementation of the distributed meteorological data processing system.
It is based on direct communication between all the components of the system using the gRPC protocol.

## Installation and execution

### Server side and sensors

To run the system, you need to have Docker and Docker Compose installed on your machine.
Refer to the [official documentation](https://docs.docker.com/engine/install/) for installation instructions.

Before running the system, ensure that the ports 50050 and 50051 are not in use.

To run the system in the background, execute the following command in the root directory of the project:

    docker compose up -d

By default, only one processing server instance is started and the two types of sensors.
If you want to start more processing server instances, you can do so by executing the following command:

    docker compose up -d --scale server=NUMBER_OF_INSTANCES

You can also start more sensors by executing the following commands

    docker compose up -d --scale air-quality-sensor=NUMBER_OF_INSTANCES
    docker compose up -d --scale pollution-sensor=NUMBER_OF_INSTANCES

To check the current status of the system, execute the following command:

    docker compose ps

To view the logs of the system, execute the following command (by default, the logs are in debug mode
so the output will be very verbose):

    docker compose logs

To stop the system, execute the following command:

    docker compose down

See the [docker official documentation](https://docs.docker.com/compose/reference/up/) for more information
and the [docker-compose.yml](docker-compose.yml) file for the configuration of the system. Most
of the configuration is specified by environment variables, which are self-explanatory.

### Terminal client

To run the terminal client you must have Python 3.8 or higher installed on your machine. Install
the required dependencies by executing the following command in the root directory of the project:

    pip install -r terminal/requirements.txt

Then you need to compile the gRPC files. To do this, execute the following command:

    make

This will generate the Python files for the gRPC communication. You can then run the terminal:

    PYTHONPATH=. python3 terminal/main.py localhost:50050 --self-address host.docker.internal --interval 2000 --debug

The `--self-address` argument is the address of the host machine. This is necessary so that the proxy
container can connect to the terminal. The `--interval` argument is the interval in milliseconds
of the tumbling window. The `--debug` argument enables debug logging.
