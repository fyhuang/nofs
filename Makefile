include $(GOROOT)/src/Make.inc

TARG=nonode
GOFILES=\
	basic_actions.go\
	http.go\
	unix_socket.go\
	nofs_node.go\

include $(GOROOT)/src/Make.cmd
