import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import time
types = {"OBJ_COMMIT" : 1, "OBJ_TREE" : 2, "OBJ_BLOB" : 3, "OBJ_TAG" : 4, "OBJ_OFS_DELTA" : 6, "OBJ_REF_DELTA" : 7 }
li = set()
commit_list = set()
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
def Binary(h):
	result = ''
	t = '\\x'
	i = 0
	if len(h) % 2 == 1:
		return 0
		print('错误，字节不为整数')
	while i < len(h):
		result += t + h[i:i+2]
		i = i + 2
	return eval('b' + '\'' + result + '\'')

def MSB_len(lenth):
	if lenth <= 15:
		return bin(lenth)[2:]
	blenth = bin(lenth)
	bnum = blenth[2:]
	while(True):
		if (len(bnum)-4) % 7 == 0:
			break
		bnum = '0' + bnum
	n = int((len(bnum)-4)/7)
	result = ''
	for i in range(0,n):
		if i == 0:
			result = '0' + bnum[(i * 7) : (i * 7 + 7)] + result
		else:
			result = '1' + bnum[(i * 7) : (i * 7 + 7)] + result
		if i == n -1 :
			result = bnum[(i+1) * 7:] + result
	return result

def write_head(pack_file, lenth):
	sha1 = hashlib.sha1()
	pack_file.write(b"PACK")
	sha1.update(b"PACK")
	pack_file.write(struct.pack('>I', 2))
	sha1.update(struct.pack('>I', 2))
	pack_file.write(struct.pack('>I',lenth))#list的大小要有限制，也就是文件数量不大于4G
	sha1.update(struct.pack('>I', lenth))
	return sha1
def head_data(lenth):
	result = b"PACK"
	result += struct.pack('>I', 2)
	result += struct.pack('>I',lenth)
	return result

def write_tail(old_name, sha1_hash):
	pack_name = sha1_hash
	os.rename(old_name ,'.git/objects/pack/pack-'  + pack_name + ".pack")
	pack_file = open('.git/objects/pack/pack-'  + pack_name + ".pack", 'ab')
	pack_file.write(Binary(pack_name))
	pack_file.close()
	os.system("git index-pack " + pack_file.name)

def obj_data(obj):
	f = obj.read_raw()
	head = 0x00 ^ (obj.type << 4)      #type
	MSB = MSB_len(len(f))
	head =  head ^ int(MSB[0:4], base = 2)
	MSB = MSB[4:]
	n = int(len(MSB) / 8)
	if n >= 1:
		head = (head ^ 0x80)
	data = struct.pack('B', head)
	for i in range(0,n):
		data += struct.pack('B', int(MSB[i*8:(i+1)*8], base = 2))
	###以上是type和长度######
	data += zlib.compress(f)
	return data

def new_pack_By_data(da, lenth):
	print(lenth, end = " ")
	print("start writing:")
	data = head_data(lenth) + da    
	sha1 = hashlib.sha1()
	sha1.update(data)
	pack_name = sha1.hexdigest()
	data += Binary(pack_name)
	pack_file = open('.git/objects/pack/pack-'  + pack_name + ".pack", 'wb')
	pack_file.write(data)
	pack_file.close()
	os.system("git index-pack " + pack_file.name)



def new_pack_By_list(object_list, repo_name):
	print(len(object_list), end = " ")
	print("start writing:")
	repo = Repository('.git')
	pack_file = open('.git/objects/pack/pack-.pack', 'wb')
	l = len(object_list)
	sha1 = write_head(pack_file, l)
	num = 0
	for file in object_list:#对每个文件写入
		num += 1
		print("\rpacking：%.2f%%" %(float(num/l*100)),end='')
		obj = repo.get(file)
		data = obj_data(obj)
		pack_file.write(data)
		sha1.update(data)
	check_sum = sha1.hexdigest()
	pack_file.close()
	print()
	write_tail(pack_file.name, check_sum)

	
def walk_commit_tree(this_commit):
	global li
	repo = Repository('.git')
	if this_commit not in li:
		li.add(this_commit)
	# data = obj_data(repo.get(this_commit))	
	queue = [repo.get(this_commit).tree]
	while len(queue) > 0:
		this_tree = queue.pop(0)
		if str(this_tree.id) in li:
			continue
		li.add(str(this_tree.id))
		# data += obj_data(this_tree)
		for t in this_tree:
			if str(t.id) in li:
				continue
			if t.type == types["OBJ_BLOB"]:
				li.add(str(t.id))
				# data += obj_data(t)
			if t.type == types["OBJ_TREE"]:
				queue.append(t)


def pack_by_commit(commit_list, repo_name, single_size = 0):
	global li
	l = len(commit_list)
	num = 0
	for commit in commit_list:
		num += 1
		print("\rcommit：%.2f%%" %(float(num/l*100)),end=' ')
		# if len(li) >= 310000:
		# 	new_pack_By_list(li, repo_name)
		# 	li = set()
		# 	print(num)
		# 	walk_commit_tree(commit)
		# 	continue
		walk_commit_tree(commit)


		if num % 20000 == 0:			
			new_pack_By_list(li, repo_name)
			break
	# new_pack_By_list(li, repo_name)





		
pack = "linux"
os.chdir(pack)


# for t in repo.get("d6b0236bd288faafd2e879fcb6677c34544322ab").tree:
# 	print(t.name)

commit_list = get_all_commit(pack)

pack_by_commit(commit_list, pack, 1<<30)




# li = get_all_objs(pack)
# new_pack_By_list(li,pack)
