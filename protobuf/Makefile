all:
	mkdir -p ../node_py/proto
	mkdir -p ../fuse_local/proto
	protoc --python_out=../node_py/proto/ *.proto
	protoc --python_out=../tools/local_proto/ *.proto
	protoc --cpp_out=../fuse_local/proto/ *.proto
