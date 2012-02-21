class FileEntry(object):
    def __init__(self, mode):
        pass

try:
    import cblockify as bl
except ImportError:
    print("Warning: optimized blockify not found, using slow Python implementation")
    import pyblockify as bl

def 
