import os
import zlib
import timeit
import pygit2
import math
from pygit2 import Repository
from pygit2 import *
import struct
import os
import hashlib
import time
import timeit
import pandas as pd #导入pandas库
import numpy as np #导入numpy库
from multiprocessing import Process
import ssdeep
from python_mmdt.mmdt.mmdt import MMDT
import libgit
import yasuo
import bsdiff
import del_instruction
import json
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
def read_pack(pa, repo_name):
	res = {}
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
					size_in_packfile = int(one[3])
					offset_in_packfile = int(one[4])
					if len(one) == 7:
						res[one[0]] = {}
						res[one[0]]["repo_name"] = repo_name	
						base_data = repo.get(one[6]).read_raw()
						src_data = repo.get(one[0]).read_raw()
						res[one[0]]["base_size"] = len(base_data)
						res[one[0]]["origin_size"] = len(src_data)
						now_delta_data = bsdiff.get_diff(base_data, src_data)
						res[one[0]]["origin_delta_size"] = int(one[2])
						res[one[0]]["now_delta_size"] = len(now_delta_data)
						res[one[0]]["origin_obj_size"] = int(one[3])
						# res[one[0]]["my_obj_size"] = len(zlib.compress(now_delta_data))
						res[one[0]]["now_obj_size"] = len(del_instruction.delta_obj_data(now_delta_data, 1, 6))#offset都取1，加快计算，误差不大
						# print(res[one[0]])
				print()
	return res
def rediff_by_repo(path, save_path):
	for fir in os.listdir(path):
		fir_dir = os.path.join(path, fir)
		for sec in os.listdir(fir_dir):
			sec_dir = os.path.join(fir_dir, sec)
			os.chdir(sec_dir)
			res = read_pack(fir_dir,sec)
			save_file = open(os.path.join(save_path ,"rediff_data.json"), 'a+')
			resjson = json.dumps(res)
			save_file.write(resjson + '\n')
def main():
	rediff_by_repo("C:\\Users\\dell\\Desktop\\git-data", "C:\\Users\\dell\\Desktop\\git_data")
main()