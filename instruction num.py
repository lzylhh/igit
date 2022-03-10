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

path = "C:\\Users\\dell\\Desktop\\bigfile"#修改包路径即可，该版本适配windows

copy_num = 0
insert_num = 0

os.chdir(path)


def read_pack_file(name,obj_size , offset_in_packfile, base_hash):
	f = open(name, 'rb')
	f.seek(offset_in_packfile, 0)
	b = f.read(1)
	typ = ((b[0] & 0x70)>>4)
	size = b[0] & 0x0f
	while((b[0] & 0x80) != 0):
		b = f.read(1)
	#以上是head
	if typ == 6:
		b = f.read(1)
		re = b[0] & 0x7f
		cishu = 0
		while((b[0] & 0x80) != 0):
			b = f.read(1)
			re += 1
			re <<= 7
			re += (b[0] & 0x7f)
		# print(re)#base negative offset
	elif typ == 7:
		base_sha1 = f.read(20)
	#delta data
	#先读取base size 和 size of the object to be reconstructed
	delta_data = f.read(obj_size - (f.tell() - offset_in_packfile))
	delta_data = zlib.decompress(delta_data)
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
	#读取恢复指令
	# base_data = repo.get(base_hash).read_raw()
	# now_data = bytes()
	num1 = 0
	num2 = 0
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
			# now_data += base_data[offset:(offset+size)]
		#新数据指令
		else:
			num2 += 1
			data_size = b&0x7f
			data = delta_data[(point+1):(point+data_size+1)]
			# now_data += data
			# print(data.decode('utf-8'))
			point += data_size
	return [num1, num2]

def read_pack():
	global copy_num
	global insert_num
	data = {}
	pack_order = "git verify-pack -v "
	for root,dirs,files in os.walk("."):
		for fn in files:
			file_name = os.path.join(root, fn)
			copy_num = 0
			insert_num = 0
			if fn.endswith(".idx"):
				data[fn] = {}
				num = 0
				lines = os.popen(pack_order + file_name).readlines()
				l = len(lines)
				for line in lines:
					num += 1 
					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
					if line.startswith("non"):
						break
					one = line.split()
					# print(one)
					# print(one[0])
					# print(one[3])
					# print(one[4])
					if len(one) == 5:
						data[fn][one[0]] = [one[1], int(one[2])]
					elif len(one) == 7:

						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
						now_data = read_pack_file(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile, one[6])
						copy_num += now_data[0]
						insert_num += now_data[1]
						# ff= open(one[0]+ ".py", "wb")
						# ff.write(now_data)
					# data[fn][one[0]].append(timeit.timeit(stmt=lambda:get_one(obj), number=1))
				print()
				print(file_name)
				print(copy_num)
				print(insert_num)
	return data
read_pack()
