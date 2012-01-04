#!/bin/bash

ORIG_CWD=`pwd`

./nofs_fuse -s mountpt/

cd mountpt
cd inbox
ls -l
cat test.txt

cd "$ORIG_CWD"
umount mountpt/
