all: build

PROTO_DIR = proto
PROTO_FILES = $(shell find $(PROTO_DIR) -name '*.proto')

clean:
	echo "Cleaning up generated files"
	rm $(shell find $(PROTO_DIR) -name '*.py')
	rm $(shell find $(PROTO_DIR) -name '*.pyi')

build: $(PROTO_FILES)
	python3 -m grpc_tools.protoc -I./ --python_out=. \
		--grpc_python_out=. --pyi_out=. $(PROTO_FILES)
