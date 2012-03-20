TARGET = libcblockify.dylib
CPPFLAGS = -O2

all: $(TARGET) test

$(TARGET): cblockify.o
	g++ -dynamiclib -o $(TARGET) cblockify.o

test.o: cblockify.cpp
	g++ $(CPPFLAGS) -c -o test.o test.cpp
test: test.o
	g++ $(CPPFLAGS) -o test test.o

clean:
	rm *.o test $(TARGET)
