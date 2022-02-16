import os
data = {}
os.chdir("test")
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
for i in data:
	for j in data[i]:
		if len(data[i][j]) == 4:
			if data[i][j][3] not in data[i]:
				print(data[i][j][3])
