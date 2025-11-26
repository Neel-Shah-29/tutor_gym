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


return_type = cloudpickle.loads(b'\x80\x05\x95\xc0\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x18numba.core.types.scalars\x94\x8c\x05Float\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x07float64\x94\x8c\x08bitwidth\x94K@\x8c\x05_code\x94K\x19u\x87\x94R\x94.')
arg_types = cloudpickle.loads(b'\x80\x05\x95\xc4\x00\x00\x00\x00\x00\x00\x00\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x18numba.core.types.scalars\x94\x8c\x05Float\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x07float64\x94\x8c\x08bitwidth\x94K@\x8c\x05_code\x94K\x19u\x87\x94R\x94h\x13\x86\x94.')
cf_type = CREFuncTypeClass(return_type, arg_types,is_composed=False, name='FloorDivide', long_hash='gkUdY3hOCqqHk32XkhjSx4XZTQOBec9DSLr8Mn0NfhE')


@lower_cast(cf_type, CREFuncType)
def upcast(context, builder, fromty, toty, val):
    return _obj_cast_codegen(context, builder, val, fromty, toty, incref=False)

call_sig = return_type(*arg_types)
call_pyfunc = cloudpickle.loads(b'\x80\x05\x95J\x02\x00\x00\x00\x00\x00\x00\x8c\x17cloudpickle.cloudpickle\x94\x8c\x0e_make_function\x94\x93\x94(h\x00\x8c\r_builtin_type\x94\x93\x94\x8c\x08CodeType\x94\x85\x94R\x94(K\x02K\x00K\x00K\x02K\x02K\x03C\x0c\x97\x00|\x00|\x01z\x02\x00\x00S\x00\x94N\x85\x94)\x8c\x01a\x94\x8c\x01b\x94\x86\x94\x8cH/home/hadoop_neel/TAIL Lab/AL_Core/apprentice/agents/cre_agents/funcs.py\x94\x8c\x0bFloorDivide\x94h\x0eK7C\r\x80\x00\xf0\x06\x00\x0c\r\x90\x01\x896\x80M\x94C\x00\x94))t\x94R\x94}\x94(\x8c\x0b__package__\x94\x8c\x1capprentice.agents.cre_agents\x94\x8c\x08__name__\x94\x8c"apprentice.agents.cre_agents.funcs\x94\x8c\x08__file__\x94h\ruNNNt\x94R\x94\x8c\x1ccloudpickle.cloudpickle_fast\x94\x8c\x12_function_setstate\x94\x93\x94h\x1a}\x94}\x94(h\x16h\x0e\x8c\x0c__qualname__\x94h\x0e\x8c\x0f__annotations__\x94}\x94\x8c\x0e__kwdefaults__\x94N\x8c\x0c__defaults__\x94N\x8c\n__module__\x94h\x17\x8c\x07__doc__\x94N\x8c\x0b__closure__\x94N\x8c\x17_cloudpickle_submodules\x94]\x94\x8c\x0b__globals__\x94}\x94u\x86\x94\x86R0.')
h0_type, h1_type,  = arg_types

call_heads = CREFunc_method(cf_type, call_sig, 'call_heads', on_error='warn')(call_pyfunc)
if(call_heads is None):
    @CREFunc_method(cf_type, call_sig, 'call_heads')
    def call_heads(a0, a1):
        with objmode(_return=return_type):
            _return = call_pyfunc(a0, a1)
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

    if(self.root_arg_infos[1].has_deref):
        var = cast(self.ref1, VarType)
        a = cast(self.a1, BaseFact)
        data_ptr = resolve_deref_data_ptr(a, var.deref_infos)
        if(data_ptr != 0):
            self.h1 = _load_ptr(h1_type, data_ptr)
        else:
            has_null_deref = True

    if(has_null_deref):
        return CFSTATUS_NULL_DEREF
    return u1(0)

@CREFunc_method(cf_type, u1(CREFuncType))
def call_self(_self):
    self = cast(_self, cf_type)

    try:
        return_val = call_heads(self.h0, self.h1)
        _store_safe(return_type, self.return_data_ptr, return_val)
        return u1(return_val > 0)
    except Exception:
        return CFSTATUS_ERROR    

# CREFunc_assign_method_addr(cf_type, 'check', -1)

# @CREFunc_method(cf_type, boolean(*arg_types))
# def match(a0, a1):
#     
#     return 1 if(call(a0, a1)) else 0

# match_heads = match
# CREFunc_assign_method_addr(cf_type, 'match_heads', match.cre_method_addr)

# @CREFunc_method(cf_type, boolean(i8[::1],))
# def match_head_ptrs(ptrs):
#     #i0 = _load_ptr(h0_type,ptrs[0])
    #i1 = _load_ptr(h1_type,ptrs[1])
#     return match_heads(i0,i1)




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
