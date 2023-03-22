import simulate
import bsdiff
def main(path):
    sortlist = simulate.get_pack_base(path)
    bsdiff.Repack(path, sortlist)
main("C:\\Users\\dell\\Desktop\\grpc")