from numba import njit, i8, u8, u4, u2
from numba.typed import Dict
from numba.types import ListType, DictType, Tuple
import numpy as np
import cloudpickle
from cre.utils import cast, _dict_from_ptr, _list_from_ptr, _get_array_raw_data_ptr
from cre.func import CFSTATUS_TRUTHY, get_return_val_impl, set_base_arg_val_impl, cre_func_resolve_call_self
from cre.sc_planner import SC_Record

ERROR_SENTINEL = 'ERROR'
typ0, = cloudpickle.loads(b'\x80\x05\x95\xbd\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x0cunicode_type\x94\x8c\x05_code\x94K\x08u\x87\x94R\x94\x85\x94.')
ret_typ = cloudpickle.loads(b'\x80\x05\x95\xbb\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x0cunicode_type\x94\x8c\x05_code\x94K\x08u\x87\x94R\x94.')
ret_d_typ = DictType(ret_typ,Tuple((i8,i8,i8)))
l_typ0 = ListType(typ0)
set_base0 = set_base_arg_val_impl(typ0)
get_ret = get_return_val_impl(ret_typ)
N_ARGS = 1

# Generic Implementation

ENTRY_WIDTH = 4+N_ARGS
@njit(cache=True)
def apply_multi(func, planner, depth):
    tup0 = (u2(4),depth)
    if(tup0 in planner.flat_vals_ptr_dict):
        iter_ptr0 = planner.flat_vals_ptr_dict[tup0]
        iter0 = _list_from_ptr(l_typ0, iter_ptr0)
    else:
        return None

    nxt_depth = depth + 1
    stride = np.array([[0,len(iter0)]],dtype=np.int64)
    val_map =  _dict_from_ptr(ret_d_typ, planner.val_map_ptr_dict[u2(4)])

    rec = SC_Record(func, nxt_depth, N_ARGS, stride)
    data = rec.data
    d_ptr = _get_array_raw_data_ptr(data)
    rec_ptr = cast(rec, i8)

    d_offset=0

    for i0 in range(stride[0][0], stride[0][1]):
        a0 = iter0[i0]
        set_base0(func,0,a0)

        status = cre_func_resolve_call_self(func)
        if(status > CFSTATUS_TRUTHY):
            continue
        v = get_ret(func)
        if v == ERROR_SENTINEL:
            continue

        low_depth, prev_low_entry, prev_entry = val_map.get(v, (-1,0,0))

        data[d_offset +0] = u4(rec_ptr) # get low bits
        data[d_offset +1] = u4(rec_ptr>>32) # get high bits
        data[d_offset +2] = u4(prev_entry) # get low bits
        data[d_offset +3] = u4(prev_entry>>32)# get high bits

        #Put arg inds at the end
        data[d_offset+4] = i0

        entry_ptr = d_ptr + d_offset*4
        if(low_depth == -1 or low_depth == nxt_depth):
            low_depth = nxt_depth
            prev_low_entry = entry_ptr

        val_map[v] = (low_depth, prev_low_entry, entry_ptr)
        d_offset += ENTRY_WIDTH
        
    return rec