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
import del_instruction
import libgit

if sys.version_info[0] == 2:
	from cStringIO import StringIO as BytesIO
else:
	from io import BytesIO

import bsdiff4.core as core
from bsdiff4.format import file_diff, file_patch, read_patch, patch

def read_data(path):
    with open(path, 'rb') as fi:
        data = fi.read()
    return data

def ddiff(src_bytes, dst_bytes):
	tcontrol, bdiff, bextra = core.diff(src_bytes, dst_bytes)
	len_dst = len(tcontrol)
	
	return len_dst, tcontrol, bdiff, bextra

def get_copy_size(offset, size):
	res = 0
	if offset <= 0xff and offset > 0:
		res += 1
	elif offset > 0xff and offset <= 0xffff:
		res += 2
	elif offset > 0xffff and offset <= 0xffffff:
		res += 3
	elif offset > 0xffffff and offset <= 0xffffffff:
		res += 4
	if size == 0x10000:
		res += 0
	elif size <= 0xff and size > 0:
		res += 1
	elif size > 0xff and size <= 0xffff:
		res += 2
	elif size > 0xffff and size <= 0xffffff:
		res += 3
	res += 1
	return res


num = 0
def get_diff(src_bytes, dst_bytes):
	global num
	len_dst, tcontrol, bdiff, bextra = ddiff(src_bytes, dst_bytes)
	len1 = len(src_bytes)
	len2 = len(dst_bytes)
	delta_data = bytearray()
	#先写入头size
	delta_data += libgit.size_format(len1)
	delta_data += libgit.size_format(len2)
	#重新编码数据
	tlist = []
	oldpos = 0
	diffpos = 0
	expos = 0
	newpos = 0
	nextra = bytearray()
	for i in range(len_dst):
		tup = tcontrol[i]
		x = tup[0]
		y = tup[1]
		z = tup[2]
		if x == 0:
			if y > 0:
				nextra += bextra[expos:expos+y]
				tlist.append([0,newpos,newpos+y])
				newpos += y
				expos += y
			oldpos += z
			continue
		#处理copy部分
		diffpoint = -1
		for j in range(x):
			#处理不一样的异样点
			if bdiff[diffpos + j] != 0:
				if diffpoint+1 < j:
					tlist.append([1,oldpos+diffpoint+1,j-diffpoint-1])#偏移和size,在两个异样点之间有的话
				c = bdiff[diffpos+j] + src_bytes[oldpos+j]
				if c > 255:
			 		c -= 256
				nextra += struct.pack('B', c)
				tlist.append([0,newpos,newpos+1])
				newpos += 1
				diffpoint = j
				continue
			if j == x-1:#遍历到末尾之后
				if diffpoint < j:
					tlist.append([1,oldpos+diffpoint+1,j-diffpoint])#偏移和size,在两个异样点之间有的话
		oldpos += x+z
		diffpos += x
		#处理新增部分
		if y > 0:
			nextra += bextra[expos:expos+y]
			tlist.append([0,newpos,newpos+y])
			newpos += y
			expos += y
	#进行数据写入
	tlen = len(tlist)
	i = 0
	while i < tlen:
		t = tlist[i]
		if t[0] == 1 and len(del_instruction.copy_format(t[1], t[2])) < t[2] + 1:
			delta_data += del_instruction.copy_format(t[1], t[2])
			i += 1
			continue
		else:
			ex_data = bytearray()
			while i < tlen:
				if tlist[i][0] == 0:
					ex_data += nextra[tlist[i][1]:tlist[i][2]]
				else:
					ex_data += src_bytes[tlist[i][1]:tlist[i][1]+tlist[i][2]]
				i += 1
				if i >= tlen:
					break
				if tlist[i][0] == 1 and len(del_instruction.copy_format(tlist[i][1], tlist[i][2])) <= tlist[i][2]:
					break
			#把所有的add数据写入
			ex_len  = len(ex_data)
			add_pos = 0
			while add_pos < ex_len:
				if add_pos + 127 < ex_len:
					delta_data += (struct.pack('B', 0x7f) + ex_data[add_pos:add_pos+127])
					add_pos += 127
				else:
					delta_data += (struct.pack('B', ex_len - add_pos) + ex_data[add_pos:ex_len])
					break
	return delta_data


	
def test(delta_data,data1,data2):
	# os.chdir(path)
	# repo = Repository(".git")
	# file1 = open("1.txt",'rb').read()
	# file2 = open("2.txt",'rb').read()
	# data2 = repo.get("00be3fcc3d9bcd662268fb008c55b4de4dda5e3a").read_raw()
	# data1 = repo.get("6f584eefc5657cc590ad5ed8863ff9e52f40a0d4").read_raw()
	# delta_data = get_diff(data1, data2)
	#验证正确性
	point = -1
	for i in range(2):
		point += 1
		b = delta_data[point]
		cishu = 0
		re = b & 0x7f
		while((b & 0x80) != 0):
			point += 1
			b = delta_data[point]
			cishu += 1
			re += ((b & 0x7f) << (cishu * 7))
		# print(re)
	now_data = bytearray()
	num1 = 0
	num2 = 0
	num3 = 0
	num4 = 0
	while(True):
		point += 1
		if point >= len(delta_data):
			break
		b = delta_data[point]
		tag = b & 0x80
		#copy指令
		if tag:
			num1 += 1
			flag = b
			offset = 0
			size = 0
			chizi = 0x01
			for i in range(4):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					offset += b<<(8*i)				
				chizi <<= 1
			for i in range(3):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					size += b<<(8*i)				
				chizi <<= 1
			now_data += data1[offset:(offset+size)]
			num3 += size
		#新数据指令
		else:
			num2 += 1
			data_size = b&0x7f
			data = delta_data[(point+1):(point+data_size+1)]
			now_data += data
			num4 += len(data)
			# print(data.decode('utf-8'))
			point += data_size
	if now_data != data2:
		return True
	return False
	# print(num3)
	# file3 = open("res.py",'wb')
	# file1 = open("1.py",'wb')
	# file2 = open("2.py",'wb')
	# file3.write(now_data)
	# file2.write(data2)
	# file1.write(data1)

def repack(path):
	os.chdir(path)
	repo = Repository(".git")
	pack_order = "git verify-pack -v "
	delta_size = 0
	new_delta_size = 0

	for root,dirs,files in os.walk(".git\\objects\\pack"):
		for fn in files:
			file_name = os.path.join(root, fn)
			if fn.endswith(".idx"):
				num = 0
				popens = os.popen(pack_order + file_name).readlines()
				lines = []
				for i in range(0,len(popens)):
					if popens[i].startswith("non"):
						break
					lines.append(popens[i].split())
				pack_file = open('.git/objects/pack/pack-.pack', 'wb')
				l = len(lines)
				sha1 = libgit.write_head(pack_file, l)
				lines.sort(key = lambda x : int(x[4]))#按照偏移量排个序
				guangbiao = 0
				offset_ji = {}
				for line in lines:
					num += 1 
					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
					one = line
					size_in_packfile = int(one[3])
					offset_in_packfile = int(one[4])
					src = repo.get(one[0]).read_raw()
					if len(one) == 5:
						# compressed_data = del_instruction.get_compressed_data(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile)[0]
						_data = libgit.obj_data(src,repo.get(one[0]).type)						
						pack_file.write(_data)
						sha1.update(_data)
						offset_ji[one[0]] = guangbiao
						guangbiao += len(_data)
					elif len(one) == 7:
						base_hash = one[6]
						delta_data = get_diff(repo.get(one[6]).read_raw(), src)
						# if test(delta_data, repo.get(one[6]).read_raw(),src):
						# 	print(one[0],one[6])
						_data = del_instruction.delta_obj_data(delta_data, guangbiao - offset_ji[one[6]], 6)
						# f = open(file_name[:-4] + ".pack",'rb')
						# delta_data = yasuo.read_delta_obj(f, size_in_packfile, offset_in_packfile, one[6])
						# delta_data = zlib.decompress(delta_data)
						# _data = del_instruction.delta_obj_data(delta_data, guangbiao - offset_ji[one[6]], 6)
						delta_size += len(_data)
						pack_file.write(_data)
						sha1.update(_data)
						offset_ji[one[0]] = guangbiao
						guangbiao += len(_data)
				check_sum = sha1.hexdigest()
				pack_file.close()
				print()
				libgit.write_tail(pack_file.name, check_sum)
				# print(delta_size)

def test1(path):
	os.chdir(path)
	repo = Repository(".git")
	# file1 = open("1.txt",'rb').read()
	# file2 = open("2.txt",'rb').read()
	data2 = repo.get("1ebb9f7cf95c1f1fcfb2b738bc3ff820a55904c6").read_raw()
	data1 = repo.get("e5d4440f31721c43a5be213e858ff6dbe165e018").read_raw()
	delta_data = get_diff(data1, data2)
	#验证正确性
	point = -1
	for i in range(2):
		point += 1
		b = delta_data[point]
		cishu = 0
		re = b & 0x7f
		while((b & 0x80) != 0):
			point += 1
			b = delta_data[point]
			cishu += 1
			re += ((b & 0x7f) << (cishu * 7))
		# print(re)
	now_data = bytearray()
	num1 = 0
	num2 = 0
	num3 = 0
	num4 = 0
	while(True):
		point += 1
		if point >= len(delta_data):
			break
		b = delta_data[point]
		tag = b & 0x80
		#copy指令
		if tag:
			num1 += 1
			flag = b
			offset = 0
			size = 0
			chizi = 0x01
			for i in range(4):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					offset += b<<(8*i)				
				chizi <<= 1
			for i in range(3):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					size += b<<(8*i)				
				chizi <<= 1
			if size == 0:
				now_data += data1[offset:(offset+0x10000)]
			else:
				now_data += data1[offset:(offset+size)]
			num3 += size
		#新数据指令
		else:
			num2 += 1
			data_size = b&0x7f
			data = delta_data[(point+1):(point+data_size+1)]
			now_data += data
			num4 += len(data)
			# print(data.decode('utf-8'))
			point += data_size
	# print(num3)
	if len(data2) != len(now_data):
		print(1)
	# l = len(data2)
	# print(l)
	# for i in range(l):
	# 	if now_data[i] != data2[i]:
	# 		print(now_data[i])
	# print(data2.decode("utf-8"))
	# nd = now_data.decode("utf-8")
	# file3 = open("res.js",'wb')
	# file1 = open("1.js",'wb')
	# file2 = open("2.js",'wb')
	# file3.write(now_data)
	# file2.write(data2)
	# file1.write(data1)

def main():
	repack("C:\\Users\\dell\\Desktop\\kubernetes")
# test1("C:\\Users\\dell\\Desktop\\three.js")
main()
# def repack1(path):
# 	os.chdir(path)
# 	repo = Repository(".git")
# 	pack_order = "git verify-pack -v "
# 	delta_size = 0
# 	new_delta_size = 0

# 	for root,dirs,files in os.walk(".git\\objects\\pack"):
# 		for fn in files:
# 			file_name = os.path.join(root, fn)
# 			if fn.endswith(".idx"):
# 				num = 0
# 				popens = os.popen(pack_order + file_name).readlines()
# 				lines = []
# 				for i in range(0,len(popens)):
# 					if popens[i].startswith("non"):
# 						break
# 					lines.append(popens[i].split())
# 				pack_file = open(file_name[:-4] + ".pack", 'rb')
# 				l = len(lines)
# 				guangbiao = 0
# 				offset_ji = {}
# 				for line in lines:
# 					num += 1 
# 					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
# 					one = line
# 					size_in_packfile = int(one[3])
# 					offset_in_packfile = int(one[4])
# 					if len(one) == 7:
						
# 						new_data = repo.get(one[0]).read_raw()
# 						origin_data = repo.get(one[6]).read_raw()
# 						new_delta_size += get_diff1(origin_data, new_data)
# 						now_data = yasuo.read_delta_obj(pack_file, size_in_packfile, offset_in_packfile, one[6])
# 						delta_size += len(now_data)
# 					if(num % 50000 == 0):
# 						print()
# 						print(delta_size)
# 						print(new_delta_size)
				
# 	print()
# 	print(delta_size)
# 	print(new_delta_size)
# repack1("C:\\Users\\dell\\Desktop\\xgboost")