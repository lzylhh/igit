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


offsets = {}
all_sizes = {}
repo = 0
def get_all_objs(repo_name):
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
		result.append(str(line[:-1]))
	return result

def get_all_commit(repo_name):
	all_commits = "git log --pretty=format:\"%H\" --all"
	result = []
	for line in os.popen(all_commits).readlines():
		result.append(str(line[:-1]))
	return result
def get_compressed_data(name,obj_size , offset_in_packfile, base_hash = "*"):
	#***首先读取所有的数据
	f = open(name, 'rb')
	f.seek(offset_in_packfile, 0)
	b = f.read(1)
	typ = ((b[0] & 0x70)>>4)
	si = b[0] & 0x0f
	cishu = 0
	qi = 0
	while((b[0] & 0x80) != 0):
		b = f.read(1)
		qi += ((b[0] & 0x7f) << (cishu * 7))
		cishu += 1
	si = si + (qi << 4)#这是数据解压后的长度

	#以上是head
	neg = b''
	if base_hash != "*":
		# print("原始字节序")
		if typ == 6:
			b = f.read(1)
			# print(bin(b[0])[2:])
			neg += b
			re = b[0] & 0x7f
			while((b[0] & 0x80) != 0):
				b = f.read(1)
				# print(bin(b[0])[2:])
				neg += b
				re += 1
				re <<= 7
				re += (b[0] & 0x7f)
			# print("包里offset")
			# print(re)#base negative offset
		elif typ == 7:
			base_sha1 = f.read(20)
	#以上类型相关
	delta_data = f.read(obj_size - (f.tell() - offset_in_packfile))
	#得到压缩数据
	return [delta_data, base_hash, neg]
def add_format(size):
	if size <= 0 or size > 127:
		raise Exception('size 应该在0到127。size 为：: {}'.format(size))
	res = struct.pack('B', size ^ 0x00)
	return res

def copy_format(offset, size):
	res = bytearray()
	biaozhi = 0x80
	if (offset & 0xff) != 0:
		res += struct.pack('B', offset & 0xff)
		biaozhi = biaozhi | 0x01
	if (offset & 0xff00) != 0:
		res += struct.pack('B', (offset & 0xff00) >> 8)
		biaozhi = biaozhi | 0x02
	if (offset & 0xff0000) != 0:
		res += struct.pack('B', (offset & 0xff0000) >> 16)
		biaozhi = biaozhi | 0x04
	if (offset & 0xff000000) != 0:
		res += struct.pack('B', (offset & 0xff000000) >> 24)
		biaozhi = biaozhi | 0x08
	if offset > 0xffffffff:
		print("字节偏移量过大，请终止程序")
	if size != 0x10000:
		if (size & 0xff) != 0:
			res += struct.pack('B', size & 0xff)
			biaozhi = biaozhi | 0x10
		if (size & 0xff00) != 0:
			res += struct.pack('B', (size & 0xff00) >> 8)
			biaozhi = biaozhi | 0x20
		if (size & 0xff0000) != 0:
			res += struct.pack('B', (size & 0xff0000) >> 16)
			biaozhi = biaozhi | 0x40
		if size > 0xffffff:
			print("体积过大，请终止程序")
	res = struct.pack('B', biaozhi) + res
	return res
	

def offset_format(offset):
	# print("原始offset")
	# print(bin(offset)[2:])
	end_len = math.ceil(len(bin(offset)[2:]) / 7)
	of = offset
	i = 1
	while(True):
		if len(bin(of)[2:]) > 7*i:
			of -= 2**(i*7)
			i += 1
		else:
			break

	bnum = bin(of)[2:]

	while(True):
		if len(bnum) % 7 == 0:
			break
		bnum = '0' + bnum

	n = int(len(bnum)/7)		
	result = ''
	for i in range(0,n):
		if i == n - 1 :
			result = result + '0' + bnum[(i * 7) : (i * 7 + 7)]
		else:
			result = result + '1' + bnum[(i * 7) : (i * 7 + 7)]
	n = len(result)//8
	res = bytearray()
	for i in range(0,n):
		res += struct.pack('B', int(result[i*8:(i+1)*8], base = 2))
	while(True):
		re = res[0] & 0x7f
		for i in range(1,len(res)):
			re += 1
			re <<= 7
			re += (res[i] & 0x7f)

		if re != offset:
			res = struct.pack('B', (0x80)) + res
		else:
			break
	# print("我写的字节序")
	# for i in res:
	# 	print(bin(i)[2:])
	return res

def del_instruction(da):
	delta_data = da[0]
	base_hash = da[1]
	delta_data = zlib.decompress(delta_data)
	res = bytearray()
	#先读取base size 和 size of the object to be reconstructed
	point = -1
	for i in range(2):
		point += 1
		b = delta_data[point]
		# print("原生")
		# print(bin(b)[2:])
		res += struct.pack('B',b)
		cishu = 0
		re = b & 0x7f
		while((b & 0x80) != 0):
			point += 1
			b = delta_data[point]
			# print(bin(b)[2:])
			res += struct.pack('B',b)
			cishu += 1
			re += ((b & 0x7f) << (cishu * 7))
		# print(re)
	#读取恢复指令并进行删减
	base_data = repo.get(base_hash).read_raw()
	order_list = []
	new_list = []
	while(True):
		point += 1
		if point >= len(delta_data):
			break
		b = delta_data[point]
		tag = b & 0x80
		if tag:
			flag = b
			offset = 0
			size = 0
			chizi = 0x01
			bytes_size = 0
			for i in range(7):
				if flag & chizi:
					bytes_size += 1
				chizi <<= 1
			copy_byte = delta_data[point:(point + bytes_size + 1)]
			chizi = 0x01
			for i in range(4):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					offset += (b<<(8*i))				
				chizi <<= 1
			for i in range(3):
				if flag & chizi:
					point += 1
					b = delta_data[point]
					size += (b<<(8*i))				
				chizi <<= 1
			if size == 0:
				size = 0x10000
			order_list.append([offset,size,0,copy_byte])
		else:
			data_size = b&0x7f
			data = delta_data[(point+1):(point+data_size+1)]
			point += data_size
			order_list.append([struct.pack('B', data_size),data,1])
	i = 0
	while(True):
		if(i+1 < len(order_list) and order_list[i][2] == 0 and order_list[i+1][2] == 0 and order_list[i+1][1]  + order_list[i][1] <= 127):
			nex = i + 1
			ex_size = order_list[i+1][1]  + order_list[i][1]
			for j in range(i+2, len(order_list)):
				if order_list[j][2] == 0:
					temp_size = order_list[j][1]
					if ex_size + temp_size < 128:
						ex_size += temp_size
						nex = j
					else:
						break
				else:
					break
			res_data = b''
			for j in range(i, nex+1):
				temp_size = order_list[j][1]
				temp_offset = order_list[j][0]
				res_data += base_data[temp_offset:(temp_offset+temp_size)]
			new_list.append([add_format(ex_size), res_data, 1])
			i = nex + 1
		elif i == len(order_list):
			break
		else:
			new_list.append(order_list[i])
			i += 1
		
	for li in new_list:
		if li[2] == 1:
			res += li[0]
			res += li[1]
		elif li[2] == 0:
			res += li[3]
	return res 

def delta_obj_data(delta_data,neg_offset, obj_type,obj_len = 0):
	data = bytearray()
	head = 0x00 ^ (obj_type << 4)
	MSB = libgit.MSB_len(len(delta_data))
	head =  head ^ int(MSB[0:4], base = 2)
	MSB = MSB[4:]
	n = int(len(MSB) / 8)
	if n >= 1:
		head = (head ^ 0x80)
	data += struct.pack('B', head)
	for i in range(0,n):
		data += struct.pack('B', int(MSB[i*8:(i+1)*8], base = 2))
	###以上是type和长度######
	###书写offset##
	offset_byte = offset_format(neg_offset)
	# offset_byte = neg_offset
	data += offset_byte
	data += zlib.compress(delta_data)
	return data


def read_pack(x_path):
	pack_order = "git verify-pack -v "
	for root,dirs,files in os.walk(x_path):
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
				l = len(lines)
				lines.sort(key = lambda x : int(x[4]))
				all_num = 0
				pack_file = open('.git/objects/pack/pack-.pack', 'wb')
				sha1 = libgit.write_head(pack_file, l)
				guangbiao = 0
				offset_ji = {}

				for line in lines:
					num += 1 
					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
					one = line
					size_in_packfile = int(one[3])
					offset_in_packfile = int(one[4])
					if len(one) == 5:
						compressed_data = get_compressed_data(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile)[0]
						_data = libgit.obj_data_test(compressed_data,repo.get(one[0]).type, len(zlib.decompress(compressed_data)))						
						pack_file.write(_data)
						sha1.update(_data)
						offset_ji[one[0]] = guangbiao
						guangbiao += len(_data)
						# if len(_data) != int(one[3]):
						# 	print(one[0])
						# 	dat = repo.get(one[0]).read_raw()
						# 	print("原始数据大小",end = ':')
						# 	print(len(dat))
						# 	print("压缩数据大小",end = ':')
						# 	print(len(zlib.compress(dat)))
						# 	print("MSB_LEN和读出来的压缩数据大小",end = ':')
						# 	print(len(get_compressed_data(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile)[0]))
						# 	print("包里数据大小和我写出来的大小",end = ':')
						# 	print(size_in_packfile)
						# 	print(len(_data))
					elif len(one) == 7:
						#以下两句自行调整，总大小得依赖于完整包环境
						compressed_delta_data = get_compressed_data(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile, one[6])
						delta_data = del_instruction(compressed_delta_data)
						# print("生成")
						# for k in libgit.size_format(len(repo.get(one[6]).read_raw())):
						# 	print(bin(k)[2:])
						# print("生成")
						# for k in libgit.size_format(len(repo.get(one[0]).read_raw())):
						# 	print(bin(k)[2:])
						_data = delta_obj_data(delta_data, guangbiao - offset_ji[one[6]], 6)
						# _data = delta_obj_data(compressed_delta_data[0], compressed_delta_data[2], 6,len(zlib.decompress(compressed_delta_data[0])))
						pack_file.write(_data)
						sha1.update(_data)
						# if len(_data) != int(one[3]):
						# 	print(one[3])
						# 	print(len(_data))
						# if compressed_delta_data[2] != offset_format(guangbiao - offset_ji[one[6]]):
						# 	print("原始offset")
						# 	print(guangbiao - offset_ji[one[6]])
						# 	print("包的字节序")
						# 	for i in compressed_delta_data[2]:
						# 		print(bin(i)[2:])
						# 	print("我写的字节序")
						# 	for i in offset_format(guangbiao - offset_ji[one[6]]):
						# 		print(bin(i)[2:])
						offset_ji[one[0]] = guangbiao
						guangbiao += len(_data)		
				check_sum = sha1.hexdigest()
				pack_file.close()
				print()
				libgit.write_tail(pack_file.name, check_sum)
def main():
	global repo
	path = "C:\\Users\\dell\\Desktop\\xgboost"#修改包路径即可，该版本适配windows
	os.chdir(path)
	repo = Repository('.git')
	read_pack(".git\\objects\\pack")