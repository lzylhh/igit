import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import time
def get_all_objs(repo_name):
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
	# if repo.get(str(line[:-1])).type == types["OBJ_BLOB"]:
		result.append(str(line[:-1]))
	return result

os.chdir("neo4j")
repo = Repository('.git')
hash_to_path = {}
path_to_hash = {}
repo = Repository('.git')
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
	for root,dirs,files in os.walk(".git/objects/pack"):
		num = 0
		l = len(files)
		for fn in files:
			num += 1
			print("\rwriting：%.2f%%" %(float(num/l*100)),end='')
			file_name = os.path.join(root, fn)
			if fn.endswith(".idx"):
				data[fn] = {}
				for line in os.popen(pack_order + file_name).readlines():
					# print(line)
					if line.startswith("non"):
						break
					one = line.split()
					if len(one) == 5:
						data[fn][one[0]] = [one[1], int(one[2])]
					elif len(one) == 7:
						data[fn][one[0]] = [one[1], int(one[2]), int(one[5]), one[6]]
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
	print(this_commit)
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
			hash_to_path[key].add(path)
			if t.type == GIT_OBJ_TREE:
				queue.append([t, path])
commits = get_all_commit("")
for c in commits:
	walk_commit_get_path(c)
num = 0
for i in hash_to_path:
	num += 1
	print(hash_to_path[i])
print(num)