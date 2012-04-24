CFLAGS=`pkg-config --cflags fuse` `pkg-config --cflags protobuf` -g -DDEBUG -Wall
CXXFLAGS=$(CFLAGS)
LDFLAGS=`pkg-config --libs fuse` `pkg-config --libs protobuf` -g

CC=g++

TARGET=fuse_local
SOURCES=$(wildcard *.cpp)
PROTO_SOURCES=$(wildcard proto/*.cc)

all: $(TARGET)
$(TARGET): $(SOURCES:.cpp=.o) $(PROTO_SOURCES:.cc=.o)

clean:
	rm *.o
	rm $(TARGET)
