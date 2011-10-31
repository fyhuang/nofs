#CFLAGS=-std=c99 -D_FILE_OFFSET_BITS=64
CFLAGS=`pkg-config --cflags fuse`
CXXFLAGS=$(CFLAGS)
#LDFLAGS=-lfuse4x
LDFLAGS=`pkg-config --libs fuse`

CC=g++

nofs_fuse: nofs_fuse.o
