import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import time
import json
import timeit
import libgit
import math
from deepdiff import DeepDiff
path = "C:\\Users\\dell\\Desktop\\g6"#修改包路径即可，该版本适配windows
blob1 = "7f5712bc7909ee1d51ea01194adc4ee56f56482c"
blob2 = "e8e11e4aa749ffa35cf5d6b02e8ad3318704c4af"
os.chdir(path)
repo = Repository('.git')
data1 = repo.get(blob1).read_raw()
data2 = repo.get(blob2).read_raw()
s = b'1r981c4yh981y481y89y38y18yc18y123112411'
ss = b'12e123e11r981c4yh981y481y812312312321e11312244gad'
res1 = {}
res2 = {}
i = 0
while i < len(s):
	res1[s[i:i+4]] = True
	i += 4
i = 0
while i < len(ss):
	res2[ss[i:i+4]] = True
	i += 4
# print(DeepDiff(res1,res2,ignore_order=True,).affected_root_keys)
diff = DeepDiff(res1,res2,ignore_order=True,ignore_encoding_errors=True)
print(diff)
print(len(diff["dictionary_item_added"]))
# print(DeepDiff(res1,res2,ignore_order=True))