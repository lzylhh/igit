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
from deepdiff import DeepDiff
from multiprocessing import Process
import ssdeep
from python_mmdt.mmdt.mmdt import MMDT
import libgit
import bsdiff
import matplotlib.pyplot as plt
from scipy import optimize
# f1 = open('1.txt','rb').read()
# f2 = open('2.txt','rb').read()
# f1 = b''
# f2 = b'0'
# hash1 = ssdeep.hash(f1)
# hash2 = ssdeep.hash(f2)
# print(ssdeep.compare(hash2, hash1))
# print(hash1)
# mmdt = MMDT()
# hash1 = mmdt.mmdt_hash()
# hash2 = mmdt.mmdt_hash('2.py')
# print(mmdt.mmdt_compare_hash(hash1, hash2))
def get_all_size_type():
    all_objs = "git cat-file --batch-check --batch-all-objects"
    sitype = {}
    res = {"commit": 1, "tree": 2, "blob": 3, "tag": 4}
    for line in os.popen(all_objs).readlines():
        l = str(line[:-1]).split()
        # if int(l[2]) == 0:
        #     print(l)
        sitype[l[0]] = [int(l[2]), res[l[1]]]
    return sitype
    
def get_all_commit():
	all_commits = "git log --pretty=format:\"%H\" --all"
	result = []
	for line in os.popen(all_commits).readlines():
		result.append(str(line[:-1]))
	return result

def get_all_name():
    all_objs = "git rev-list --objects  --all"
    result = {}
    for line in os.popen(all_objs).readlines():
        l = str(line[:-1]).split()
        result[l[0]] = l[1:]
        obj = l[0]
        for i in range(len(result[obj])):
            result[obj][i] = result[obj][i].split('/')[-1]
        # if len(l) > 2:
        #     print(result[l[0]])
    return result

def f_1(x, a, b):
	return a*x + b
def test(path):
    os.chdir(path)
    repo = Repository(".git")
    all_obj = libgit.get_all_objs("")
    hash_res = {}
    hash_data = {}
    x = []
    y = []
    f = open("C:\\Users\\dell\\Desktop\\igit\\ssdeep.txt",'a+')
    
    for obj in all_obj:
        data = repo.get(obj).read_raw()
        hash_data[obj] = data
        hash_res[obj] = ssdeep.hash(data)
    hash_res = list(hash_res.items())
    num = 0
    for i in range(len(hash_res)-1):
        p = 0
        print(i)
        
        for j in range(i+1, len(hash_res)):
            cmp_hash = ssdeep.compare(hash_res[i][1], hash_res[j][1])
            dst = hash_data[hash_res[i][0]]
            src = hash_data[hash_res[j][0]]
            if cmp_hash > 0:
                delta_data = bsdiff.get_diff(src, dst)
                x.append(cmp_hash)
                y.append(len(delta_data)/len(dst))
        # if p > 2:
        #     num += 1
    f.write(str(x) + '*')
    f.write(str(y) + '*')
    plt.figure()
    plt.scatter(x, y, 0.01)
    a1, b1 = optimize.curve_fit(f_1, x, y)[0]
    x1 = np.array(x)
    y1 = a1*x1 + b1
    plt.plot(x1, y1, 'black')
    plt.xlabel('Ssdeep similar')
    plt.ylabel('Compression ratio')
    plt.show()
# test("C:\\Users\\dell\\Desktop\\gin")
def testpack(path):
    os.chdir(path)
    repo = Repository(".git")
    pack_order = "git verify-pack -v "
    all_obj = libgit.get_all_objs("")
    x = []
    y = []
    for root,dirs,files in os.walk(".git\\objects\\pack"):
        for fn in files:
            file_name = os.path.join(root, fn)
            if fn.endswith(".idx"):
                num = 0
                popens = os.popen(pack_order + file_name).readlines()
                lines = []
                for i in range(0,len(popens)):
                    if popens[i].startswith("non"):
                        break
                    lines.append(popens[i].split())
                pack_file = open('.git/objects/pack/pack-.pack', 'wb')
                l = len(lines)
                for line in lines:
                    num += 1 
                    print("\rreading：%.2f%%" %(float(num/l*100)),end='')
                    one = line
                    size_in_packfile = int(one[3])
                    offset_in_packfile = int(one[4])
                    if len(one) == 7:
                        dst = repo.get(one[0]).read_raw()
                        src = repo.get(one[6]).read_raw()
                        delta_data = bsdiff.get_diff(src, dst)
                        hash1 = ssdeep.hash(src)
                        hash2 = ssdeep.hash(dst)
                        x.append(ssdeep.compare(hash1,hash2))
                        y.append(len(delta_data)/len(dst))
                        if ssdeep.compare(hash1,hash2) == 0:
                            p = 0
                            for obj in all_obj:
                                data = repo.get(obj).read_raw()
                                hashs = ssdeep.hash(data)
                                if ssdeep.compare(hashs,hash2) > 0:
                                    p = 1
                                    x.append(ssdeep.compare(hashs,hash2))
                                    y.append(len(bsdiff.get_diff(data, dst))/len(dst))
                                    # print(ssdeep.compare(hash1,hash2), len(src), len(dst),len(delta_data), len(delta_data)/len(dst))
                                    # print(ssdeep.compare(hashs,hash2), len(data), len(dst),len(bsdiff.get_diff(data, dst)), len(bsdiff.get_diff(data, dst))/len(dst))
                            if p == 0:
                                print(1)
                        # print(ssdeep.compare(hash1,hash2), len(src), len(dst),len(delta_data), len(delta_data)/len(dst))
                print()
    plt.scatter(x, y)
    plt.show()
# testpack("C:\\Users\\dell\\Desktop\\gin")

visited = {}#0代表没有进行访问，1代表访问中，2代表已经进入最终队列，3代表没有相似的对象：待定状态
def shunxu( liebiao):
    global  visited
    sortlist = {}
    def dfs(s):
        global visited
        nonlocal sortlist
        nex = liebiao[s]
        visited[s] = 1
        if len(nex) == 0:
            visited[s] = 3
            return
        for j in nex:
            if visited[j] == 0:
                dfs(j)
                if visited[j] == 2:
                    sortlist[s] = j
                elif visited[j] == 3:
                    sortlist[j] = ""
                    visited[j] = 2
                    sortlist[s] = j
                visited[s] = 2
                return
            elif visited[j] == 1:
                continue
            elif visited[j] == 2:
                sortlist[s] = j
                visited[s] = 2
                return
            elif visited[j] == 3:
                sortlist[j] = ""
                visited[j] = 2
                sortlist[s] = j
                visited[s] = 2
                return
        sortlist[s] = ""
        visited[s] = 2
        return
    for i in liebiao:
        if visited[i] == 0:
            dfs(i)
    base = ""
    if len(sortlist) > 0:
        for s in sortlist:
            base = s
            break
    for i in liebiao:
        # if visited[i] == 3 and base != "":
        #     sortlist[i] = base
        #     visited[i] = 2
        # elif visited[i] == 3 and base == "":
        #     sortlist[i] = ""
        #     visited[i] = 2
        if visited[i] == 3:
            sortlist[i] = ""
            visited[i] = 2
    # print(len(liebiao))
    # print(len(sortlist))
    # print()
    # print(liebiao)
    # print(sortlist)
    # print()
    return sortlist
    

def get_pack_base(path):
    global visited
    visited = {}
    result = {}
    os.chdir(path)
    repo = Repository(".git")
    sitype = get_all_size_type()
    all_name = get_all_name()
    noname = {}
    name2blobhash = {}
    name2treehash = {}
    name2taghash = {}
    ssdeep_hash = {}
    num = 0
    l = len(all_name)
    for obj in all_name:
        num += 1
        print("\rreading objects：%.2f%%" %(float(num/l*100)),end='')
        visited[obj] = 0
        ssdeep_hash[obj] = ssdeep.hash(repo.get(obj).read_raw())
        if len(all_name[obj]) == 0:
            noname[obj] = sitype[obj]
        else:
            names = all_name[obj]
            for _name in names:
                if sitype[obj][1] == 2:
                    if _name not in  name2treehash:
                        name2treehash[_name] = {}
                        name2treehash[_name][obj] = sitype[obj][0]
                    else:
                        name2treehash[_name][obj] = sitype[obj][0]
                if sitype[obj][1] == 3:
                    if _name not in  name2blobhash:
                        name2blobhash[_name] = {}
                        name2blobhash[_name][obj] = sitype[obj][0]
                    else:
                        name2blobhash[_name][obj] = sitype[obj][0]
                if sitype[obj][1] == 4:
                    if _name not in  name2taghash:
                        name2taghash[_name] = {}
                        name2taghash[_name][obj] = sitype[obj][0]
                    else:
                        name2taghash[_name][obj] = sitype[obj][0]
                
    print()
    commits = {}
    trees = {}
    blob = {}
    tags = {}
    #没有名字的
    for obj in noname:
        if sitype[obj][1] == 1:
            commits[obj] = sitype[obj][0]
        elif sitype[obj][1] == 2:
            trees[obj] = sitype[obj][0]
        elif sitype[obj][1] == 3:
            blob[obj] = sitype[obj][0]
        elif sitype[obj][1] == 4:
            tags[obj] = sitype[obj][0]
    commits = sorted(commits.items(), key = lambda x:x[1])
    for i in range(0,len(commits), 100):#每50个一组
        j = 0
        if i + 100 < len(commits):
            j = i+100
        else:
            j = len(commits)
        liebiao = {}
        for t in range(i,j):
            liebiao[commits[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[commits[t][0]], ssdeep_hash[commits[k][0]])
                if simi > 0:
                    liebiao[commits[t][0]].append([commits[k][0],simi])
                    liebiao[commits[k][0]].append([commits[t][0],simi])
        for t in range(i,j):
            temp = liebiao[commits[t][0]]
            liebiao[commits[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[commits[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        # print(sortlist)
        for obj in sortlist:
            result[obj] = sortlist[obj]
    blob = sorted(blob.items(), key = lambda x:x[1])
    for i in range(0,len(blob), 100):#每50个一组
        j = 0
        if i + 100 < len(blob):
            j = i+100
        else:
            j = len(blob)
        liebiao = {}
        for t in range(i,j):
            liebiao[blob[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[blob[t][0]], ssdeep_hash[blob[k][0]])
                if simi > 0:
                    liebiao[blob[t][0]].append([blob[k][0],simi])
                    liebiao[blob[k][0]].append([blob[t][0],simi])
        for t in range(i,j):
            temp = liebiao[blob[t][0]]
            liebiao[blob[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[blob[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        # print(sortlist)
        for obj in sortlist:
            result[obj] = sortlist[obj]
    trees = sorted(trees.items(), key = lambda x:x[1])
    for i in range(0,len(trees), 100):#每50个一组
        j = 0
        if i + 100 < len(trees):
            j = i+100
        else:
            j = len(trees)
        liebiao = {}
        for t in range(i,j):
            liebiao[trees[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[trees[t][0]], ssdeep_hash[trees[k][0]])
                if simi > 0:
                    liebiao[trees[t][0]].append([trees[k][0],simi])
                    liebiao[trees[k][0]].append([trees[t][0],simi])
        for t in range(i,j):
            temp = liebiao[trees[t][0]]
            liebiao[trees[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[trees[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        for obj in sortlist:
            result[obj] = sortlist[obj]
    tags = sorted(tags.items(), key = lambda x:x[1])
    for i in range(0,len(tags), 100):#每50个一组
        j = 0
        if i + 100 < len(tags):
            j = i+100
        else:
            j = len(tags)
        liebiao = {}
        for t in range(i,j):
            liebiao[tags[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[tags[t][0]], ssdeep_hash[tags[k][0]])
                if simi > 0:
                    liebiao[tags[t][0]].append([tags[k][0],simi])
                    liebiao[tags[k][0]].append([tags[t][0],simi])
        for t in range(i,j):
            temp = liebiao[tags[t][0]]
            liebiao[tags[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[tags[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        for obj in sortlist:
            result[obj] = sortlist[obj]

    # nobase = {}
    # linshi = {}
    # for _name in name2taghash:
    #     quyu = name2taghash[_name]
    #     quyu = sorted(quyu.items(), key = lambda x:x[1])
    #     for i in range(0,len(quyu), 500):#每500个一组
    #         j = 0
    #         if i + 500 < len(quyu):
    #             j = i + 500
    #         else:
    #             j = len(quyu)
    #         liebiao = {}
    #         for t in range(i,j):
    #             liebiao[quyu[t][0]] = []
    #         for t in range(i,j-1):
    #             for k in range(t+1, j):
    #                 simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #                 if simi > 0:
    #                     liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                     liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #         for t in range(i,j):
    #             temp = liebiao[quyu[t][0]]
    #             liebiao[quyu[t][0]] = []
    #             temp.sort(key=lambda x:-x[1])
    #             for item in temp:
    #                 liebiao[quyu[t][0]].append(item[0])
    #         sortlist = shunxu(liebiao)
    #         for obj in sortlist:
    #             base = sortlist[obj]
    #             if base == "":
    #                 nobase[obj] = name2taghash[_name][obj]
    #             linshi[obj] = base
    # quyu = nobase
    # quyu = sorted(quyu.items(), key = lambda x:x[1])
    # for i in range(0,len(quyu), 500):#每500个一组
    #     j = 0
    #     if i + 500 < len(quyu):
    #         j = i + 500
    #     else:
    #         j = len(quyu)
    #     liebiao = {}
    #     for t in range(i,j):
    #         liebiao[quyu[t][0]] = []
    #         visited[quyu[t][0]] = 0
    #     for t in range(i,j-1):
    #         for k in range(t+1, j):
    #             simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #             if simi > 0:
    #                 liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                 liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #     for t in range(i,j):
    #         temp = liebiao[quyu[t][0]]
    #         liebiao[quyu[t][0]] = []
    #         temp.sort(key=lambda x:-x[1])
    #         for item in temp:
    #             liebiao[quyu[t][0]].append(item[0])
    #     sortlist = shunxu(liebiao)
    #     for obj in sortlist:
    #         result[obj] = sortlist[obj]
    # for obj in linshi:
    #     result[obj] = linshi[obj]

    # linshi = {}
    # nobase = {}
    # for _name in name2treehash:
    #     quyu = name2treehash[_name]
    #     quyu = sorted(quyu.items(), key = lambda x:x[1])
    #     for i in range(0,len(quyu), 500):#每500个一组
    #         j = 0
    #         if i + 500 < len(quyu):
    #             j = i + 500
    #         else:
    #             j = len(quyu)
    #         liebiao = {}
    #         for t in range(i,j):
    #             liebiao[quyu[t][0]] = []
    #         for t in range(i,j-1):
    #             for k in range(t+1, j):
    #                 simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #                 if simi > 0:
    #                     liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                     liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #         for t in range(i,j):
    #             temp = liebiao[quyu[t][0]]
    #             liebiao[quyu[t][0]] = []
    #             temp.sort(key=lambda x:-x[1])
    #             for item in temp:
    #                 liebiao[quyu[t][0]].append(item[0])
    #         sortlist = shunxu(liebiao)
    #         for obj in sortlist:
    #             base = sortlist[obj]
    #             if base == "":
    #                 nobase[obj] = name2treehash[_name][obj]
    #             linshi[obj] = base
    # quyu = nobase
    # quyu = sorted(quyu.items(), key = lambda x:x[1])
    # for i in range(0,len(quyu), 500):#每500个一组
    #     j = 0
    #     if i + 500 < len(quyu):
    #         j = i + 500
    #     else:
    #         j = len(quyu)
    #     liebiao = {}
    #     for t in range(i,j):
    #         liebiao[quyu[t][0]] = []
    #         visited[quyu[t][0]] = 0
    #     for t in range(i,j-1):
    #         for k in range(t+1, j):
    #             simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #             if simi > 0:
    #                 liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                 liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #     for t in range(i,j):
    #         temp = liebiao[quyu[t][0]]
    #         liebiao[quyu[t][0]] = []
    #         temp.sort(key=lambda x:-x[1])
    #         for item in temp:
    #             liebiao[quyu[t][0]].append(item[0])
    #     sortlist = shunxu(liebiao)
    #     for obj in sortlist:
    #         result[obj] = sortlist[obj]
    # for obj in linshi:
    #     result[obj] = linshi[obj]
    
    # nobase = {}
    # linshi ={}
    # for _name in name2blobhash:
    #     quyu = name2blobhash[_name]
    #     quyu = sorted(quyu.items(), key = lambda x:x[1])
    #     for i in range(0,len(quyu), 500):#每500个一组
    #         j = 0
    #         if i + 500 < len(quyu):
    #             j = i + 500
    #         else:
    #             j = len(quyu)
    #         liebiao = {}
    #         for t in range(i,j):
    #             liebiao[quyu[t][0]] = []
    #         for t in range(i,j-1):
    #             for k in range(t+1, j):
    #                 simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #                 if simi > 0:
    #                     liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                     liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #         for t in range(i,j):
    #             temp = liebiao[quyu[t][0]]
    #             liebiao[quyu[t][0]] = []
    #             temp.sort(key=lambda x:-x[1])
    #             for item in temp:
    #                 liebiao[quyu[t][0]].append(item[0])
    #         sortlist = shunxu(liebiao)
    #         for obj in sortlist:
    #             base = sortlist[obj]
    #             if base == "":
    #                 nobase[obj] = name2blobhash[_name][obj]
    #             linshi[obj] = base
    # quyu = nobase
    # quyu = sorted(quyu.items(), key = lambda x:x[1])
    # for i in range(0,len(quyu), 500):#每500个一组
    #     j = 0
    #     if i + 500 < len(quyu):
    #         j = i + 500
    #     else:
    #         j = len(quyu)
    #     liebiao = {}
    #     for t in range(i,j):
    #         liebiao[quyu[t][0]] = []
    #         visited[quyu[t][0]] = 0
    #     for t in range(i,j-1):
    #         for k in range(t+1, j):
    #             simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
    #             if simi > 0:
    #                 liebiao[quyu[t][0]].append([quyu[k][0],simi])
    #                 liebiao[quyu[k][0]].append([quyu[t][0],simi])
    #     for t in range(i,j):
    #         temp = liebiao[quyu[t][0]]
    #         liebiao[quyu[t][0]] = []
    #         temp.sort(key=lambda x:-x[1])
    #         for item in temp:
    #             liebiao[quyu[t][0]].append(item[0])
    #     sortlist = shunxu(liebiao)
    #     for obj in sortlist:
    #         result[obj] = sortlist[obj]
    # for obj in linshi:
    #     result[obj] = linshi[obj]


    jishuqi = 0
    quyu = {}
    for _name in name2treehash:
        this_one = name2treehash[_name]
        this_len = len(this_one)
        if jishuqi + this_len < 500:
            for th in this_one:
                quyu[th] = this_one[th]
            jishuqi += this_len
            continue            
        quyu = sorted(quyu.items(), key = lambda x:x[1])
        for i in range(0,len(quyu), 500):#每500个一组
            j = 0
            if i + 500 < len(quyu):
                j = i + 500
            else:
                j = len(quyu)
            liebiao = {}
            for t in range(i,j):
                liebiao[quyu[t][0]] = []
            for t in range(i,j-1):
                for k in range(t+1, j):
                    simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                    if simi > 0:
                        liebiao[quyu[t][0]].append([quyu[k][0],simi])
                        liebiao[quyu[k][0]].append([quyu[t][0],simi])
            for t in range(i,j):
                temp = liebiao[quyu[t][0]]
                liebiao[quyu[t][0]] = []
                temp.sort(key=lambda x:-x[1])
                # print(temp)
                for item in temp:
                    liebiao[quyu[t][0]].append(item[0])
            sortlist = shunxu(liebiao)
            for obj in sortlist:
                result[obj] = sortlist[obj]
        jishuqi = this_len
        quyu = this_one
    quyu = sorted(quyu.items(), key = lambda x:x[1])
    for i in range(0,len(quyu), 500):#每500个一组
        j = 0
        if i + 500 < len(quyu):
            j = i + 500
        else:
            j = len(quyu)
        liebiao = {}
        for t in range(i,j):
            liebiao[quyu[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                if simi > 0:
                    liebiao[quyu[t][0]].append([quyu[k][0],simi])
                    liebiao[quyu[k][0]].append([quyu[t][0],simi])
        for t in range(i,j):
            temp = liebiao[quyu[t][0]]
            liebiao[quyu[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[quyu[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        for obj in sortlist:
            result[obj] = sortlist[obj]

    jishuqi = 0
    quyu = {}
    for _name in name2blobhash:
        this_one = name2blobhash[_name]
        this_len = len(this_one)
        if jishuqi + this_len < 500:
            for th in this_one:
                quyu[th] = this_one[th]
            jishuqi += this_len
            continue            
        quyu = sorted(quyu.items(), key = lambda x:x[1])
        for i in range(0,len(quyu), 500):#每500个一组
            j = 0
            if i + 500 < len(quyu):
                j = i + 500
            else:
                j = len(quyu)
            liebiao = {}
            for t in range(i,j):
                liebiao[quyu[t][0]] = []
            for t in range(i,j-1):
                for k in range(t+1, j):
                    simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                    if simi > 0:
                        liebiao[quyu[t][0]].append([quyu[k][0],simi])
                        liebiao[quyu[k][0]].append([quyu[t][0],simi])
            for t in range(i,j):
                temp = liebiao[quyu[t][0]]
                liebiao[quyu[t][0]] = []
                temp.sort(key=lambda x:-x[1])
                # print(temp)
                for item in temp:
                    liebiao[quyu[t][0]].append(item[0])
            sortlist = shunxu(liebiao)
            for obj in sortlist:
                result[obj] = sortlist[obj]
        jishuqi = this_len
        quyu = this_one
    quyu = sorted(quyu.items(), key = lambda x:x[1])
    for i in range(0,len(quyu), 500):#每500个一组
        j = 0
        if i + 500 < len(quyu):
            j = i + 500
        else:
            j = len(quyu)
        liebiao = {}
        for t in range(i,j):
            liebiao[quyu[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                if simi > 0:
                    liebiao[quyu[t][0]].append([quyu[k][0],simi])
                    liebiao[quyu[k][0]].append([quyu[t][0],simi])
        for t in range(i,j):
            temp = liebiao[quyu[t][0]]
            liebiao[quyu[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[quyu[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        for obj in sortlist:
            result[obj] = sortlist[obj]

    jishuqi = 0
    quyu = {}
    for _name in name2taghash:
        this_one = name2taghash[_name]
        this_len = len(this_one)
        if jishuqi + this_len < 500:
            for th in this_one:
                quyu[th] = this_one[th]
            jishuqi += this_len
            continue            
        quyu = sorted(quyu.items(), key = lambda x:x[1])
        for i in range(0,len(quyu), 500):#每500个一组
            j = 0
            if i + 500 < len(quyu):
                j = i + 500
            else:
                j = len(quyu)
            liebiao = {}
            for t in range(i,j):
                liebiao[quyu[t][0]] = []
            for t in range(i,j-1):
                for k in range(t+1, j):
                    simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                    if simi > 0:
                        liebiao[quyu[t][0]].append([quyu[k][0],simi])
                        liebiao[quyu[k][0]].append([quyu[t][0],simi])
            for t in range(i,j):
                temp = liebiao[quyu[t][0]]
                liebiao[quyu[t][0]] = []
                temp.sort(key=lambda x:-x[1])
                # print(temp)
                for item in temp:
                    liebiao[quyu[t][0]].append(item[0])
            sortlist = shunxu(liebiao)
            for obj in sortlist:
                result[obj] = sortlist[obj]
        jishuqi = this_len
        quyu = this_one
    quyu = sorted(quyu.items(), key = lambda x:x[1])
    for i in range(0,len(quyu), 500):#每500个一组
        j = 0
        if i + 500 < len(quyu):
            j = i + 500
        else:
            j = len(quyu)
        liebiao = {}
        for t in range(i,j):
            liebiao[quyu[t][0]] = []
        for t in range(i,j-1):
            for k in range(t+1, j):
                simi = ssdeep.compare(ssdeep_hash[quyu[t][0]], ssdeep_hash[quyu[k][0]])
                if simi > 0:
                    liebiao[quyu[t][0]].append([quyu[k][0],simi])
                    liebiao[quyu[k][0]].append([quyu[t][0],simi])
        for t in range(i,j):
            temp = liebiao[quyu[t][0]]
            liebiao[quyu[t][0]] = []
            temp.sort(key=lambda x:-x[1])
            # print(temp)
            for item in temp:
                liebiao[quyu[t][0]].append(item[0])
        sortlist = shunxu(liebiao)
        for obj in sortlist:
            result[obj] = sortlist[obj]

    jiance = {}
    re = 0
    for r in result:
        if result[r] != "":
            re += 1
            if result[r] not in jiance:
                print("error")
        jiance[r] = ""
    print(re,len(all_name),re/len(all_name))
    return result
            
# get_pack_base("C:\\Users\\dell\\Desktop\\d3")