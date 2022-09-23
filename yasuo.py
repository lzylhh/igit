import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import time
import timeit
import random
import matplotlib.pyplot as plt
import json
from deepdiff import DeepDiff
PATH = "C:\\Users\\dell\\Desktop\\git-data"
SPATH = "C:\\Users\\dell\\Desktop\\git_data"
res = {}
def get_all_objs(repo_name):
	os.chdir(repo_name)
	all_objs = "git rev-list --objects --no-object-names --all"
	result = []
	for line in os.popen(all_objs).readlines():
		result.append(str(line[:-1]))
	return result
def get_all_size(repo_name):
	os.chdir(repo_name)
	all_objs = "git cat-file --batch-check --batch-all-objects"
	result = {}
	for line in os.popen(all_objs).readlines():
		l = str(line[:-1]).split()
		result[l[0]] = int(l[2])
	return result

def read_delta_obj(f, obj_size_in_pf, offset_in_packfile, base_hash):
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
	delta_data = f.read(obj_size_in_pf - (f.tell() - offset_in_packfile))
	return delta_data
def read_origin_obj(f, obj_size_in_pf, offset_in_packfile):
	f.seek(offset_in_packfile, 0)
	b = f.read(1)
	typ = ((b[0] & 0x70)>>4)
	size = b[0] & 0x0f
	while((b[0] & 0x80) != 0):
		b = f.read(1)
	#以上是head
	ori_data = f.read(obj_size_in_pf - (f.tell() - offset_in_packfile))
	return ori_data

def read_pack(pa, repo_name):
	global res
	pack_order = "git verify-pack -v "
	repo = Repository(os.path.join(pa, repo_name, ".git"))
	for root,dirs,files in os.walk(".git\\objects\\pack"):
		for fn in files:
			file_name = os.path.join(root, fn)
			if fn.endswith(".idx"):
				print(repo_name + file_name)
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
					res[one[0]] = {}
					res[one[0]]["repo_name"] = repo_name
					res[one[0]]["origin_size"] = int(one[2])
					res[one[0]]["size_in_packfile"] = int(one[3])
					if len(one) == 5:
						res[one[0]]["is_delta"] = 0
						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
						now_data = read_origin_obj(pack_file ,size_in_packfile,offset_in_packfile)
						for level in range(1,10):
							com_data = zlib.compress(now_data, level)
							size = len(com_data)
							time = timeit.timeit(stmt=lambda:zlib.compress(now_data, level), number=1)
							res[one[0]]["level_" + str(level) + "_time"] = time
							res[one[0]]["level_" + str(level) + "_size"] = size
					elif len(one) == 7:
						res[one[0]]["is_delta"] = 1
						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
						now_data = read_delta_obj(pack_file, size_in_packfile, offset_in_packfile, one[6])
						for level in range(1,10):
							com_data = zlib.compress(now_data, level)
							size = len(com_data)
							time = timeit.timeit(stmt=lambda:zlib.compress(now_data, level), number=1)
							res[one[0]]["level_" + str(level) + "_time"] = time
							res[one[0]]["level_" + str(level) + "_size"] = size
				print()

def compress_by_repo(path, save_path):
	global res
	for fir in os.listdir(path):
		fir_dir = os.path.join(path, fir)
		for sec in os.listdir(fir_dir):
			sec_dir = os.path.join(fir_dir, sec)
			os.chdir(sec_dir)
			li = get_all_objs(sec_dir)
			all_size = get_all_size(sec_dir)
			l = len(li)
			res = {}
			read_pack(fir_dir,sec)
			save_file = open(os.path.join(save_path ,"origin_data.json"), 'a+')
			resjson = json.dumps(res)
			save_file.write(resjson + '\n')
def compress_by_file(repo_name):
	os.chdir(repo_name)
	repo =  Repository(".git")
	li = get_all_objs(repo_name)
	all_size = get_all_size(repo_name)
	for level in range(0,10):
		time = 0
		size = 0
		sizes = []
		times = []
		for obj in li:
			obj_data = repo.get(obj).read_raw()
			size += all_size[obj]
			time += timeit.timeit(stmt=lambda:zlib.compress(obj_data, level), number=1)
			sizes.append(size)
			times.append(time)
		plt.scatter(sizes, times, c='red', label='time')
		plt.xlabel("size", fontdict={'size': 16})
		plt.ylabel("time", fontdict={'size': 16})
		plt.title("size-time in zlib compress with level " + str(level), fontdict={'size': 20})
		plt.legend(loc='best')
		plt.show()
def read_pack2(pa, repo_name):
	global res
	pack_order = "git verify-pack -v "
	repo = Repository(os.path.join(pa, repo_name, ".git"))
	for root,dirs,files in os.walk(".git\\objects\\pack"):
		for fn in files:
			file_name = os.path.join(root, fn)
			if fn.endswith(".idx"):
				print(repo_name + "   " +file_name)
				num = 0
				lines = os.popen(pack_order + file_name).readlines()
				pack_file = open( file_name[:-4] + ".pack",'rb')
				l = len(lines)
				delta_size = 0
				for line in lines:
					num += 1 
					print("\rreading：%.2f%%" %(float(num/l*100)),end='')
					if line.startswith("non"):
						break
					one = line.split()
					if len(one) == 7:
						size_in_packfile = int(one[3])
						offset_in_packfile = int(one[4])
				
						now_data = repo.get(one[0]).read_raw()
						origin_data = repo.get(one[6]).read_raw()
						res1 = {}
						res2 = {}
						i = 0
						while i < len(origin_data) - 4:
							res1[origin_data[i:i+4]] = True
							i += 1
						i = 0
						while i < len(now_data):
							res2[now_data[i:i+4]] = True
							i += 4
						# print(DeepDiff(res1,res2,ignore_order=True,).affected_root_keys)
						diff = DeepDiff(res1,res2,ignore_order=True,ignore_encoding_errors=True)
						if "dictionary_item_added" in diff:
							delta_size += len(diff["dictionary_item_added"])
				print(delta_size*4)

						
				print()
def compress_by_repo2(path):
	global res
	for fir in os.listdir(path):
		fir_dir = os.path.join(path, fir)
		for sec in os.listdir(fir_dir):
			if sec != "scrcpy":
				continue
			sec_dir = os.path.join(fir_dir, sec)
			os.chdir(sec_dir)
			li = get_all_objs(sec_dir)
			all_size = get_all_size(sec_dir)
			l = len(li)
			res = {}
			read_pack2(fir_dir,sec)
compress_by_repo2(PATH)

