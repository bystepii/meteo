#!/bin/bash
# This script compiles all the proto files in the proto directory (--compile)
# or cleans up the generated files (--clean)

if [ "$1" == "--clean" ]; then
    echo "Cleaning up generated files"
    rm -rf $(find proto -name '*.py')
    rm -rf $(find proto -name '*.pyi')
elif [ "$1" == "--compile" ]; then
    echo "Compiling proto files"
    python -m grpc_tools.protoc -I./ --python_out=. \
        --grpc_python_out=. --pyi_out=. $(find proto -name '*.proto')
else
    echo "Usage: $0 [--clean|--compile]"
    exit 1
fi
