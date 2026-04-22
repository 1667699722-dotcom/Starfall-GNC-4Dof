import ctypes
import numpy as np
import gc
lib = ctypes.CDLL("./link.dylib")

lib.link.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float)
]
keep_alive = None
keep_alive_dict={}
def clink(arr):
    global keep_alive_dict
    arr = np.asarray(arr, dtype=np.float32)
    n=int(arr[0])
    out = ctypes.c_float()
    match n:
        case 0:
            lib.link(0, None,None)
            return 0
        case 1:
            val = ctypes.c_float(arr[1])
            keep_alive_dict["val"]=val
            lib.link(1, ctypes.byref(val),None)
            if "val" in keep_alive_dict:
                del keep_alive_dict["val"]
                gc.collect()
            return 0
        case 2:
            lib.link(2, None, ctypes.byref(out))
            return out.value

