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
SPATH = "C:\\Users\\dell\\Desktop\\git_data"
def analyze(save_path):
	save_file = open(os.path.join(save_path ,"origin_data.json"), encoding='utf-8')
	for line in save_file.readlines():
		res = json.loads(line)
		sum_size = 0
		level_size = [0]*11
		level_time = [0]*11
		level_dtime = [0]*11
		repo_name = ""
		for obj in res:

			repo_name = res[obj]["rname"]
			sum_size += res[obj]["o_size"]
			for level in range(1,10):
				
				level_size[level] += res[obj][str(level)][0]
				level_time[level] += res[obj][str(level)][1]
				level_dtime[level] += res[obj][str(level)][2]
		for level in range(1,10):
			print(repo_name + "  " + str(level) + "  " + str(float(sum_size)/1000) + "  " +  str(float(level_size[level])/float(sum_size)) + "  " + str(level_time[level]) + "  " + str(level_dtime[level]))
analyze(SPATH)