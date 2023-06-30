import simulate
import bsdiff
import time
import timeit
import sys
import bsdiff
def main(path):
    sortlist = simulate.get_pack_base(path)
    bsdiff.Repack(path, sortlist)
if __name__ == '__main__':
    # print(sys.argv)
    if len(sys.argv) == 3:
        if sys.argv[1] == '-f':
            bsdiff.repack(sys.argv[2])
        else:
            print("Wrong Input")
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Wrong Input")
# print(timeit.timeit(stmt=lambda:main("C:\\Users\\dell\\Desktop\\server"), number=1))