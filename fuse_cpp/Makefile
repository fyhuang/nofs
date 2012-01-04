CFLAGS=`pkg-config --cflags fuse` -g -DDEBUG -Wall
CXXFLAGS=$(CFLAGS)
LDFLAGS=`pkg-config --libs fuse` -g

CC=g++

SOURCES=$(wildcard *.cpp)

all: nofs_fuse
nofs_fuse: $(SOURCES:.cpp=.o)

clean:
	rm *.o
	rm nofs_fuse
