import pygit2
from pygit2 import Repository
from pygit2 import *
import binascii
import zlib
import struct
import os
import hashlib
import random
import time
import timeit
import random
import matplotlib.pyplot as plt
import json
import pandas as pd #导入pandas库
import numpy as np #导入numpy库
from sklearn.linear_model import LinearRegression

SPATH = "C:\\Users\\dell\\Desktop\\git_data"
def analyze(save_path):
	save_file = open(os.path.join(save_path ,"origin_data.json"), encoding='utf-8')
	obj_li = []
	data = {}
	for level in range(1,10):
		data["x" + str(level)] = []
		data["y" + str(level)] = []
		data["z" + str(level)] = []
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
				# data["x" + str(level)].append(res[obj]["o_size"])
				# data["y" + str(level)].append(res[obj][str(level)][1])
				# data["z" + str(level)].append(res[obj][str(level)][2])
				level_size[level] += res[obj][str(level)][0]
				level_time[level] += res[obj][str(level)][1]
				level_dtime[level] += res[obj][str(level)][2] 
		for level in range(1,10):
			# data["x" + str(level)].append(sum_size)
			# data["y" + str(level)].append(level_time[level])
			# data["z" + str(level)].append(level_dtime[level])
			print(repo_name + "  " + str(level) + "  " + str(float(sum_size)/1000) + "  " +  str(float(level_size[level])/float(sum_size)) + "  " + str(level_time[level]) + "  " + str(level_dtime[level]))
	# for level in range(1,10):
	# 	x = np.array(data["x" + str(level)]).reshape(-1,1)
	# 	y = np.array(data["y" + str(level)])
	# 	z = np.array(data["z" + str(level)])
	# 	regr1=LinearRegression(fit_intercept=False)
	# 	regr2=LinearRegression(fit_intercept=False)
	# 	regr1.fit(x,y)
	# 	regr2.fit(x,z)
	# 	print(str(level) + "  a  " + str(regr1.coef_) + "  b  " + str(regr1.intercept_))
	# 	print(regr1.score(x, y))
	# 	print(str(level) + "  a  " + str(regr2.coef_) + "  b  " + str(regr2.intercept_))
	# 	print(regr2.score(x, z))
def analyze2(save_path):
	save_file = open(os.path.join(save_path ,"zlib_yasuo_data.json"), encoding='utf-8')
	# for line in save_file.readlines():
	# 	res = json.loads(line)
	# 	obj_num = 0
	# 	del_num = 0
	# 	for obj in res:
	# 		repo_name = res[obj]["rname"]
	# 		obj_num += 1
	# 		if res[obj]["del?"] == 1:
	# 			del_num += 1
	# 	print(repo_name + "  " + str(obj_num) + "  "+ str(del_num) + "  " + str(del_num/obj_num))
	sum_size = 0
	level_size = [0]*11
	level_time = [0]*11
	level_dtime = [0]*11
	repo_name = ""
	for line in save_file.readlines():
		res = json.loads(line)

		print(repo_name)
		for obj in res:

			repo_name = res[obj]["rname"]
			
			sum_size += res[obj]["o_size"]
			for level in range(1,10):
				level_size[level] += res[obj][str(level)][0]
				level_time[level] += res[obj][str(level)][1]
				level_dtime[level] += res[obj][str(level)][2] 
	for level in range(1,10):
		print(str(level) + "  " + str(sum_size) + "  " +  str(float(level_size[level])/float(sum_size)) + "  " + str(level_time[level]) + "  " + str(level_dtime[level]))
analyze2(SPATH)