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
arg_types = cloudpickle.loads(b'\x80\x05\x95\xbd\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x0cunicode_type\x94\x8c\x05_code\x94K\x08u\x87\x94R\x94\x85\x94.')
cf_type = CREFuncTypeClass(return_type, arg_types,is_composed=False, name='apply_pythagorean', long_hash='dlN3AsrAVNRGLZnwJbOPmRSGwOdTetnQzo9ct4pFAks')


@lower_cast(cf_type, CREFuncType)
def upcast(context, builder, fromty, toty, val):
    return _obj_cast_codegen(context, builder, val, fromty, toty, incref=False)

call_sig = return_type(*arg_types)
call_pyfunc = cloudpickle.loads(b'\x80\x05\x95b\x04\x00\x00\x00\x00\x00\x00\x8c\x17cloudpickle.cloudpickle\x94\x8c\x0e_make_function\x94\x93\x94(h\x00\x8c\r_builtin_type\x94\x93\x94\x8c\x08CodeType\x94\x85\x94R\x94(K\x01K\x00K\x00K\x07K\x05K\x03B\x04\x01\x00\x00\x97\x00d\x01d\x02l\x00m\x01}\x01\x01\x00t\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|\x00\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00}\x02|\x02\xa0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00d\x03\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00}\x03|\x02\xa0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00d\x04\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00}\x04|\x03\x81\x02|\x04\x80\x07t\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00S\x00t\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00j\x06\x00\x00\x00\x00\x00\x00\x00\x00|\x03|\x03z\x05\x00\x00|\x04|\x04z\x05\x00\x00z\x00\x00\x00\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00}\x05\x02\x00|\x01|\x05\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00}\x06t\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|\x06\xa6\x01\x00\x00\xab\x01\x00\x00\x00\x00\x00\x00\x00\x00S\x00\x94(NK\x00\x8c\x05latex\x94\x85\x94\x8c\x01a\x94\x8c\x01b\x94t\x94(\x8c\x05sympy\x94h\t\x8c\x0b_parse_vals\x94\x8c\x03get\x94\x8c\x0eERROR_SENTINEL\x94\x8c\x02sp\x94\x8c\x04sqrt\x94\x8c\x03str\x94t\x94(\x8c\ninit_value\x94h\t\x8c\x04vals\x94h\x0bh\x0c\x8c\x01c\x94\x8c\x04hint\x94t\x94\x8cH/home/hadoop_neel/TAIL Lab/AL_Core/apprentice/agents/cre_agents/funcs.py\x94\x8c\x11apply_pythagorean\x94h\x1cK\xf8C\x82\x80\x00\xe0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xd0\x04\x1b\xdd\x0b\x16\x90z\xd1\x0b"\xd4\x0b"\x80D\xd8\x08\x0c\x8f\x08\x8a\x08\x90\x13\x89\r\x8c\r\x80A\xd8\x08\x0c\x8f\x08\x8a\x08\x90\x13\x89\r\x8c\r\x80A\xd8\x07\x08\x80y\x90A\x90I\xdd\x0f\x1d\xd0\x08\x1d\xdd\x08\n\x8c\x07\x90\x01\x90!\x91\x03\x90a\x98\x01\x91c\x91\t\xd1\x08\x1a\xd4\x08\x1a\x80A\xe0\x0b\x10\x885\x90\x11\x898\x8c8\x80D\xdd\x0b\x0e\x88t\x899\x8c9\xd0\x04\x14\x94C\x00\x94))t\x94R\x94}\x94(\x8c\x0b__package__\x94\x8c\x1capprentice.agents.cre_agents\x94\x8c\x08__name__\x94\x8c"apprentice.agents.cre_agents.funcs\x94\x8c\x08__file__\x94h\x1buNNNt\x94R\x94\x8c\x1ccloudpickle.cloudpickle_fast\x94\x8c\x12_function_setstate\x94\x93\x94h(}\x94}\x94(h$h\x1c\x8c\x0c__qualname__\x94h\x1c\x8c\x0f__annotations__\x94}\x94\x8c\x0e__kwdefaults__\x94N\x8c\x0c__defaults__\x94N\x8c\n__module__\x94h%\x8c\x07__doc__\x94N\x8c\x0b__closure__\x94N\x8c\x17_cloudpickle_submodules\x94]\x94\x8c\x0b__globals__\x94}\x94(h\x0fh%h\x0f\x93\x94h\x11\x8c\x05ERROR\x94h\x12h\x00\x8c\tsubimport\x94\x93\x94h\x0e\x85\x94R\x94uu\x86\x94\x86R0.')
h0_type,  = arg_types

call_heads = CREFunc_method(cf_type, call_sig, 'call_heads', on_error='none')(call_pyfunc)
if(call_heads is None):
    @CREFunc_method(cf_type, call_sig, 'call_heads')
    def call_heads(a0):
        with objmode(_return=return_type):
            _return = call_pyfunc(a0)
        return _return

@CREFunc_method(cf_type, u1(CREFuncType))
def resolve_heads(_self):
    self = cast(_self, cf_type)
    has_null_deref = False
    
    if(self.root_arg_infos[0].has_deref):
        var = cast(self.ref0, VarType)
        a = cast(self.a0, BaseFact)
        data_ptr = resolve_deref_data_ptr(a, var.deref_infos)
        if(data_ptr != 0):
            self.h0 = _load_ptr(h0_type, data_ptr)
        else:
            has_null_deref = True

    if(has_null_deref):
        return CFSTATUS_NULL_DEREF
    return u1(0)

@CREFunc_method(cf_type, u1(CREFuncType))
def call_self(_self):
    self = cast(_self, cf_type)

    try:
        return_val = call_heads(self.h0)
        _store_safe(return_type, self.return_data_ptr, return_val)
        return CFSTATUS_TRUTHY if(return_val) else CFSTATUS_FALSEY
    except Exception:
        return CFSTATUS_ERROR    

# CREFunc_assign_method_addr(cf_type, 'check', -1)

# @CREFunc_method(cf_type, boolean(*arg_types))
# def match(a0):
#     
#     return 1 if(call(a0)) else 0

# match_heads = match
# CREFunc_assign_method_addr(cf_type, 'match_heads', match.cre_method_addr)

# @CREFunc_method(cf_type, boolean(i8[::1],))
# def match_head_ptrs(ptrs):
#     #i0 = _load_ptr(h0_type,ptrs[0])
#     return match_heads(i0)




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
