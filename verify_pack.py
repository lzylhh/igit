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

path = "C:\\Users\\dell\\Desktop\\test"#修改包路径即可，该版本适配windows

def get_all_objs(repo_name):
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
	# if repo.get(str(line[:-1])).type == types["OBJ_BLOB"]:
		result.append(str(line[:-1]))
	return result

os.chdir(path)
repo = Repository('.git')
hash_to_path = {}
path_to_hash = {}
repo = Repository('.git')
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
					if len(one) == 5:
						data[fn][one[0]] = [one[1], int(one[2])]
					elif len(one) == 7:
						data[fn][one[0]] = [one[1], int(one[2]), int(one[5]), one[6]]
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