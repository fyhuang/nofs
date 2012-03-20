TARGET = libcblockify.dylib
CPPFLAGS = -O2
LDFLAGS = -O2

all: $(TARGET) test

$(TARGET): cblockify.o sha2.o
	g++ -dynamiclib $(LDFLAGS) -o $(TARGET) cblockify.o sha2.o

test.o: cblockify.cpp
	g++ $(CPPFLAGS) -c -o test.o test.cpp
test: test.o sha2.o
	g++ $(CPPFLAGS) $(LDFLAGS) -o test test.o sha2.o

clean:
	rm *.o test $(TARGET)
