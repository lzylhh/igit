import simulate
import bsdiff
import time
import timeit
def main(path):
    sortlist = simulate.get_pack_base(path)
    bsdiff.Repack(path, sortlist)
print(timeit.timeit(stmt=lambda:main("C:\\Users\\dell\\Desktop\\pandas"), number=1))