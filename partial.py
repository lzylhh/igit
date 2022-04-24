import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import time
path = "C:\\Users\\dell\\Desktop\\neo4j"#修改包路径即可，该版本适配windows
os.chdir(path)
repo = Repository('.git')
hash_to_path = {}
path_to_hash = {}
commit_list = set()
def get_all_objs(repo_name):
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
	# if repo.get(str(line[:-1])).type == types["OBJ_BLOB"]:
		result.append(str(line[:-1]))
	return result
def get_all_commit(repo_name):
	all_commits = "git log --pretty=format:\"%H\" --all"
	result = []
	for line in os.popen(all_commits).readlines():
		result.append(str(line[:-1]))
	return result
def walk_commit_get_path(this_commit):
	global hash_to_path
	global path_to_hash
	global repo
	hash_to_path[str(this_commit)]= set()
	hash_to_path[str(repo.get(this_commit).tree.id)]= set()
	queue = [[repo.get(this_commit).tree, ""]]
	while len(queue) > 0:
		two = queue.pop(0)
		this_tree = two[0]
		for t in this_tree:
			if t.name == None:
				print(t.type)
				path = ""
			else:
				if two[1] != "":
					path = two[1] + '/' + t.name
				else:
					path = t.name
			key = str(t.id)
			try:
				if key in hash_to_path:
					hash_to_path[key].add(path)
				else:
					hash_to_path[key] = set()
					hash_to_path[key].add(path)
			except Exception as e:
				print("continue")
			if t.type == GIT_OBJ_TREE:
				queue.append([t, path])
def baohan(path,path_set):
	for p in path_set:
		if path in p:
			return True
	return False
def dengyu(path,path_set):
	for p in path_set:
		if path == p:
			return True
	return False
commits = get_all_commit("")
n = 1
for c in commits:
	walk_commit_get_path(c)
	n += 1
	if n == 2:
		break
os.chdir("C:\\Users\\dell\\Desktop")
if not os.path.exists("neo4jj"):
	os.mkdir("neo4jj")
os.chdir("C:\\Users\\dell\\Desktop\\neo4jj")
os.system("git init")
reppo = Repository('.git')
for h in hash_to_path:
	obj = repo.get(h)
	if obj.type == GIT_OBJ_BLOB:
		if baohan("annotations/" ,hash_to_path[h]) or baohan(".gitignore", hash_to_path[h]) or baohan(".gitattributes", hash_to_path[h]):
			reppo.write(obj.type,obj.read_raw())
		else:
			dirr = h[0:2]
			blob_name = h[2:]
			dir_path = os.getcwd()+"\\.git\\objects\\" + dirr
			if os.path.exists(dir_path):
				open(dir_path + "\\" + blob_name,"w")
			else:
				os.mkdir(dir_path)
				open(dir_path + "\\" + blob_name,"w")

	elif obj.type == GIT_OBJ_COMMIT or GIT_OBJ_TREE:
		reppo.write(obj.type,obj.read_raw())
