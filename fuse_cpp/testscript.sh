#!/bin/bash

ORIG_CWD=`pwd`

./nofs_fuse -s mountpt/

cd mountpt
cd inbox
ls -l
#time bash copyn.sh 1000 pic.jpg "$ORIG_CWD/"
cp pic.jpg "$ORIG_CWD/"
#cd testdir
#ls -l
#cat largefile.txt

cd "$ORIG_CWD"
umount mountpt/

open pic.jpg
