import ctypes
import numpy as np
import gc
lib = ctypes.CDLL("./bin/link.dylib")

lib.link.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_void_p)
]
out =  ctypes.c_void_p()
keep_alive_dict={}
def clink(arr):
    global keep_alive_dict
    arr = np.asarray(arr, dtype=np.float32)
    n=int(arr[0])
    match n:
        case 0:
            lib.link(0, None,None)
            return 0
        case 1:
            val = (ctypes.c_float*3)(arr[1],arr[2],arr[3])
            keep_alive_dict["val"]=val
            lib.link(1, val,None)
            if "val" in keep_alive_dict:
                del keep_alive_dict["val"]
                gc.collect()
            return 0
        case 2:
            #lib.link(2, None, ctypes.byref(out))
            lib.link(2, None,ctypes.byref(out))
            ptr = ctypes.cast(out, ctypes.POINTER(ctypes.c_float*3))
            #loat_ptr = ctypes.cast(ctypes.byref(out), ctypes.POINTER(ctypes.c_float))
            return  ptr.contents

