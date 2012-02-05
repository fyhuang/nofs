CFLAGS=`pkg-config --cflags fuse` -g -DDEBUG -Wall
CXXFLAGS=$(CFLAGS)
LDFLAGS=`pkg-config --libs fuse` -g

CC=g++

TARGET=fuse_local
SOURCES=$(wildcard *.cpp)

all: $(TARGET)
$(TARGET): $(SOURCES:.cpp=.o)

clean:
	rm *.o
	rm $(TARGET)
