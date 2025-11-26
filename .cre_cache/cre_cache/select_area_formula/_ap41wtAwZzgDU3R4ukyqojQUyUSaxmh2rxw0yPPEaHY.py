import numpy as np
from numba import njit, void, i8, u1, boolean, objmode
from numba.types import unicode_type
from numba.extending import lower_cast
from numba.core.errors import NumbaError, NumbaPerformanceWarning
from cre.utils import _incref_structref, cast, PrintElapse, _load_ptr, _obj_cast_codegen, _store_safe, _struct_get_attr_ptr
from cre.func import (ensure_repr_const, get_cre_func_ctor_data, CREFunc_method, CREFunc_assign_method_addr,
    CREFuncTypeClass, CREFuncType, VarType, CFSTATUS_TRUTHY, CFSTATUS_FALSEY, CFSTATUS_NULL_DEREF, CFSTATUS_ERROR)
from cre.fact import BaseFact, resolve_deref_data_ptr
import cloudpickle


return_type = cloudpickle.loads(b'\x80\x05\x95\xbb\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x0cunicode_type\x94\x8c\x05_code\x94K\x08u\x87\x94R\x94.')
arg_types = cloudpickle.loads(b'\x80\x05).')
cf_type = CREFuncTypeClass(return_type, arg_types,is_composed=False, name='select_area_formula', long_hash='ap41wtAwZzgDU3R4ukyqojQUyUSaxmh2rxw0yPPEaHY')


@lower_cast(cf_type, CREFuncType)
def upcast(context, builder, fromty, toty, val):
    return _obj_cast_codegen(context, builder, val, fromty, toty, incref=False)

call_sig = return_type(*arg_types)
call_pyfunc = cloudpickle.loads(b'\x80\x05\x95\x8e\x02\x00\x00\x00\x00\x00\x00\x8c\x17cloudpickle.cloudpickle\x94\x8c\x0e_make_function\x94\x93\x94(h\x00\x8c\r_builtin_type\x94\x93\x94\x8c\x08CodeType\x94\x85\x94R\x94(K\x00K\x00K\x00K\x01K\x02K\x03C\x12\x97\x00d\x01d\x02l\x00m\x01}\x00\x01\x00d\x03S\x00\x94(NK\x00\x8c\x05latex\x94\x85\x94\x8c\x111/2\xc2\xb7a\xc2\xb7b\xc2\xb7sin(C)\x94t\x94\x8c\x05sympy\x94h\t\x86\x94h\t\x85\x94\x8cH/home/hadoop_neel/TAIL Lab/AL_Core/apprentice/agents/cre_agents/funcs.py\x94\x8c\x13select_area_formula\x94h\x11Mw\x01C\x1c\x80\x00\xe0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xf0\x06\x00\x0c\x1f\xd0\x0b\x1e\x94C\x00\x94))t\x94R\x94}\x94(\x8c\x0b__package__\x94\x8c\x1capprentice.agents.cre_agents\x94\x8c\x08__name__\x94\x8c"apprentice.agents.cre_agents.funcs\x94\x8c\x08__file__\x94h\x10uNNNt\x94R\x94\x8c\x1ccloudpickle.cloudpickle_fast\x94\x8c\x12_function_setstate\x94\x93\x94h\x1d}\x94}\x94(h\x19h\x11\x8c\x0c__qualname__\x94h\x11\x8c\x0f__annotations__\x94}\x94\x8c\x0e__kwdefaults__\x94N\x8c\x0c__defaults__\x94N\x8c\n__module__\x94h\x1a\x8c\x07__doc__\x94N\x8c\x0b__closure__\x94N\x8c\x17_cloudpickle_submodules\x94]\x94\x8c\x0b__globals__\x94}\x94u\x86\x94\x86R0.')


call_heads = CREFunc_method(cf_type, call_sig, 'call_heads', on_error='none')(call_pyfunc)
if(call_heads is None):
    @CREFunc_method(cf_type, call_sig, 'call_heads')
    def call_heads():
        with objmode(_return=return_type):
            _return = call_pyfunc()
        return _return

@CREFunc_method(cf_type, u1(CREFuncType))
def resolve_heads(_self):
    self = cast(_self, cf_type)
    has_null_deref = False
    
    if(has_null_deref):
        return CFSTATUS_NULL_DEREF
    return u1(0)

@CREFunc_method(cf_type, u1(CREFuncType))
def call_self(_self):
    self = cast(_self, cf_type)

    try:
        return_val = call_heads()
        _store_safe(return_type, self.return_data_ptr, return_val)
        return CFSTATUS_TRUTHY if(return_val) else CFSTATUS_FALSEY
    except Exception:
        return CFSTATUS_ERROR    

# CREFunc_assign_method_addr(cf_type, 'check', -1)

# @CREFunc_method(cf_type, boolean(*arg_types))
# def match():
#     
#     return 1 if(call()) else 0

# match_heads = match
# CREFunc_assign_method_addr(cf_type, 'match_heads', match.cre_method_addr)

# @CREFunc_method(cf_type, boolean(i8[::1],))
# def match_head_ptrs(ptrs):
# 
#     return match_heads()




# Make sure that constant members can be repr'ed
for at in arg_types:
    ensure_repr_const(at)

# ctor = gen_cre_func_ctor(cf_type)

# @njit(CREFuncType(unicode_type, unicode_type, unicode_type), cache=True)
# def ctor(name, expr_template, shorthand_template):
#     return cre_func_ctor(cf_type, name, expr_template, shorthand_template, False)

ctor, method_addrs = get_cre_func_ctor_data(cf_type)
cf_type.ctor = ctor
cf_type.method_addrs = method_addrs
cf_type.uses_ptr_args = False
