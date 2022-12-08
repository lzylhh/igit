from __future__ import absolute_import

import bz2
import sys

from bsdiff4 import diff, patch, file_diff, file_patch, file_patch_inplace
if sys.version_info[0] == 2:
    from cStringIO import StringIO as BytesIO
else:
    from io import BytesIO

MAGIC = b'BSDIFF40'
def read_patch(fi, header_only=False):
    """read a BSDIFF4-format patch from stream 'fi'
    """
    magic = fi.read(8)
    assert magic[:7] == MAGIC[:7]
    # length headers
    len_control = core.decode_int64(fi.read(8))
    len_diff = core.decode_int64(fi.read(8))
    len_dst = core.decode_int64(fi.read(8))
    # read the control header
    bcontrol = bz2.decompress(fi.read(len_control))
    tcontrol = [(core.decode_int64(bcontrol[i:i + 8]),
                 core.decode_int64(bcontrol[i + 8:i + 16]),
                 core.decode_int64(bcontrol[i + 16:i + 24]))
                for i in range(0, len(bcontrol), 24)]
    if header_only:
        return len_control, len_diff, len_dst, tcontrol
    # read the diff and extra blocks
    bdiff = bz2.decompress(fi.read(len_diff))
    bextra = bz2.decompress(fi.read())
    return len_dst, tcontrol, bdiff, bextra
def read_data(path):
    with open(path, 'rb') as fi:
        data = fi.read()
    return data

