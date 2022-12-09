import bz2
import sys
import struct
import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import os
import hashlib
import time
import timeit
import random
import yasuo

if sys.version_info[0] == 2:
	from cStringIO import StringIO as BytesIO
else:
	from io import BytesIO

MAGIC = b'BSDIFF40'
import bsdiff4.core as core
from bsdiff4.format import file_diff, file_patch, read_patch, patch

def read_data(path):
    with open(path, 'rb') as fi:
        data = fi.read()
    return data

def ddiff(src_bytes, dst_bytes):
	tcontrol, bdiff, bextra = core.diff(src_bytes, dst_bytes)
	len_dst = len(dst_bytes)
	
	return len_dst, tcontrol, bdiff, bextra

def get_copy_size(offset, size):
	res = 0
	if offset <= 0xff:
		res += 1
	elif offset > 0xff and offset <= 0xffff:
		res += 2
	elif offset > 0xffff and offset <= 0xffffff:
		res += 3
	elif offset > 0xffffff and offset <= 0xffffffff:
		res += 4
	if size == 0x10000:
		res += 0
	elif size <= 0xff:
		res += 1
	elif offset > 0xff and offset <= 0xffff:
		res += 2
	elif offset > 0xffff and offset <= 0xffffff:
		res += 3
	res += 1
	return res

def get_diff(src_bytes, dst_bytes):
	len_dst, tcontrol, bdiff, bextra = ddiff(src_bytes, dst_bytes)
	# d = open("diff", 'rb')
	# len_dst, tcontrol, bdiff, bextra = read_patch(d)
	l = len(tcontrol)
	
	oldpos = 0
	diffpos = 0
	expos = 0
	newdata = bytearray(b'')
	oldata = bytearray(src_bytes)
	num = 0
	i = 0
	final = 0
	while i < l:
		tup = tcontrol[i]
		x = tup[0]
		y = tup[1]
		z = tup[2]	
		if x == 0:
			oldpos += z
			final += y
			i += 1
			continue
		copy = bytearray(b'')
		offset = oldpos
		size = x
		copy_size = get_copy_size(offset, size)
		if copy_size >= size + 1:
			lianxu = 0
			while i < l:
				lianxu += tcontrol[i][0]
				oldpos += tcontrol[i][0] + tcontrol[i][2]
				i += 1
				if i >= l:
					break
				cs = get_copy_size(oldpos, tcontrol[i][0])
				if cs < tcontrol[i][0]:
					break
			exa = lianxu // 127
			final += lianxu + exa + 1
		else:
			final += copy_size
			# for j in range(x):
			# 	# newdata  += core.encode_int64(bdiff[diffpos+j])
			# 	c = bdiff[diffpos+j]+oldata[oldpos+j]
			# 	if c > 255:
			# 		c -= 256
			# 	copy  += struct.pack('B', bdiff[diffpos+j]+oldata[oldpos+j])
			# newdata += copy
			# diffpos += x
			oldpos += x

			# final += y

			# newdata += bextra[expos: expos + y]
			# expos += y

			oldpos += z
			i += 1
	return final

def test_neo4j():
	os.chdir("C:\\Users\\dell\\Desktop\\neo4j")
	repo = Repository(".git")
	pack_order = "git verify-pack -v "
	delta_size = 0
	new_delta_size = 0
	for root,dirs,files in os.walk(".git\\objects\\pack"):
		for fn in files:
			file_name = os.path.join(root, fn)
			if fn.endswith(".idx"):
				num = 0
				lines = os.popen(pack_order + file_name).readlines()
				pack_file = open( file_name[:-4] + ".pack",'rb')
				l = len(lines)
				for line in lines:
					num += 1 
					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
					if line.startswith("non"):
						break
					one = line.split()
					if len(one) == 7:
						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
				
						new_data = repo.get(one[0]).read_raw()
						origin_data = repo.get(one[6]).read_raw()
						new_delta_size += get_diff(origin_data, new_data)
						now_data = yasuo.read_delta_obj(pack_file, size_in_packfile, offset_in_packfile, one[6])
						delta_size += len(zlib.decompress(now_data))
					if(num % 50000 == 0):
						print()
						print(delta_size)
						print(new_delta_size)
	print()
	print(delta_size)
	print(new_delta_size)					
	
test_neo4j()
