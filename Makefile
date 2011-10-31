include $(GOROOT)/src/Make.inc

TARG=nonode
GOFILES=\
	nofs.go\
	buffers.go\
	basic_actions.go\
	http.go\
	byte_ring.go\
	unix_socket.go\
	nofs_node.go\

include $(GOROOT)/src/Make.cmd
