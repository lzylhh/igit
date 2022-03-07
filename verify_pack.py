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

path = "C:\\Users\\dell\\Desktop\\igit"#修改包路径即可，该版本适配windows

def get_all_objs(repo_name):
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
		result.append(str(line[:-1]))
	return result
def get_all_size(repo_name):
	all_objs = "git cat-file --batch-check --batch-all-objects"
	result = {}
	for line in os.popen(all_objs).readlines():
		l = str(line[:-1]).split()
		result[l[0]] = int(l[2])
	return result

os.chdir(path)
repo = Repository('.git')
hash_to_path = {}
path_to_hash = {}
all_sizes = get_all_size("")
def get_one(hash):
	return repo.get(hash).read_raw()
for obj in get_all_objs(''):
	hash_to_path[obj] = set()

def get_all_commit(repo_name):
	all_commits = "git log --pretty=format:\"%H\" --all"
	result = []
	
	for line in os.popen(all_commits).readlines():
		result.append(str(line[:-1]))
	return result
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
		# print(re)#base nagetive offset
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
		# print(re)
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
			# print(offset)
			# print(size)
		#新数据指令
		else:
			num2 += 1
			data_size = b&0x7f
			# print(data_size)
			data = delta_data[(point+1):(point+data_size+1)]
			# now_data += data
			# print(data.decode('utf-8'))
			point += data_size
	return [num1, num2]

def read_pack():
	data = {}
	pack_order = "git verify-pack -v "
	for root,dirs,files in os.walk(".git\\objects\\pack"):
		for fn in files:
			file_name = os.path.join(root, fn)
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

						data[fn][one[0]] = [one[1], all_sizes[one[0]], int(one[5]), one[6]]
						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
						now_data = read_pack_file(file_name[:-4] + ".pack", size_in_packfile, offset_in_packfile, one[6])
						data[fn][one[0]].append(now_data[0])
						data[fn][one[0]].append(now_data[1])
						# ff= open(one[0]+ ".py", "wb")
						# ff.write(now_data)
					# data[fn][one[0]].append(timeit.timeit(stmt=lambda:get_one(obj), number=1))
				print()
	return data
# for i in data:
# 	for j in data[i]:
# 		if len(data[i][j]) == 4:
# 			if data[i][j][3] not in data[i]:
# 				print(data[i][j][3])

def walk_commit_get_path(this_commit):
	global hash_to_path
	global path_to_hash
	global repo
	queue = [[repo.get(this_commit).tree, ""]]
	while len(queue) > 0:
		two = queue.pop(0)
		this_tree = two[0]
		for t in this_tree:
			if t.name == None:
				path = ""
			else:
				if two[1] != "":
					path = two[1] + '/' + t.name
				else:
					path = t.name
			key = str(t.id)
			try:
				hash_to_path[key].add(path)
			except:
				print("continue")
			if t.type == GIT_OBJ_TREE:
				queue.append([t, path])
commits = get_all_commit("")
l = len(commits)
print(str(l) + " commits start scanning:")
num = 0 
for c in commits:
	walk_commit_get_path(c)
	num += 1
	print("\rscanning：%.2f%%" %(float(num/l*100)),end='')
print()
for i in hash_to_path:
	hash_to_path[i] = list(hash_to_path[i])
pack_data  = read_pack()
with open(".git\\objects\\pack\\pack_data.json", "w") as f:
	json.dump(pack_data,f)
with open(".git\\objects\\pack\\hash_to_path.json", "w") as f:
	json.dump(hash_to_path,f)