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
import pandas as pd #导入pandas库
import numpy as np #导入numpy库
from sklearn.linear_model import LinearRegression
SPATH = "C:\\Users\\dell\\Desktop\\git_data"


def analyze(save_path):
	save_file = open(os.path.join(save_path ,"rediff_data.json"), encoding='utf-8')
	data1 = [[],[],[],[],[],[],[],[]]
	data2 = [[],[],[],[],[],[],[],[]]
	for line in save_file.readlines():
		res = json.loads(line)
		for obj in res:
			base_size = res[obj]["base_size"]
			origin_size = res[obj]["origin_size"]
			origin_delta_size = res[obj]["origin_delta_size"]
			now_delta_size = res[obj]["now_delta_size"]
			origin_obj_size = res[obj]["origin_obj_size"]
			now_obj_size = res[obj]["now_obj_size"]
			num1 = float(now_delta_size-origin_delta_size)/float(origin_delta_size)
			num2 = float(now_obj_size-origin_obj_size)/float(origin_obj_size)
			if origin_size > 0 and origin_size < 100:
				data1[0].append(num1)
				data2[0].append(num2)
			elif origin_size >= 100 and origin_size < 1000:
				data1[1].append(num1)
				data2[1].append(num2)
			elif origin_size >= 1000 and origin_size < 10000:
				data1[2].append(num1)
				data2[2].append(num2)
			elif origin_size >= 10000 and origin_size < 100000:
				data1[3].append(num1)
				data2[3].append(num2)
			elif origin_size >= 100000 and origin_size < 1000000:
				data1[4].append(num1)
				data2[4].append(num2)
			elif origin_size >= 1000000 and origin_size < 2000000:
				data1[5].append(num1)
				data2[5].append(num2)
			elif origin_size >= 2000000 and origin_size < 5000000:
				data1[6].append(num1)
				data2[6].append(num2)
			elif origin_size >= 5000000:
				data1[7].append(num1)
				data2[7].append(num2)
	view = plt.boxplot(data1,labels = ["0-0.1K", "0.1K-1K", "1K-10K", "10K-100K", "100K-1M", "1M-2M", "2M-5M", ">5M"],showfliers = False)
	plt.xlabel('File size')
	plt.ylabel('Compression ratio descend')
	plt.show()
	view = plt.boxplot(data2,labels = ["0-0.1K", "0.1K-1K", "1K-10K", "10K-100K", "100K-1M", "1M-2M", "2M-5M", ">5M"],showfliers = False)
	plt.xlabel('File size')
	plt.ylabel('Compression ratio descend')
	plt.show()
analyze(SPATH)