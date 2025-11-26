
import numpy as np
from numba.core import types
from numba import njit, literally, literal_unroll
from numba.core.types import *
from numba.core.types import unicode_type, ListType, UniTuple, Tuple
from numba.experimental import structref
from numba.experimental.structref import new#, define_boxing
from numba.core.extending import overload, overload_method, lower_cast, type_callable
from numba.core.imputils import numba_typeref_ctor
from cre.fact_intrinsics import define_boxing, get_fact_attr_ptr, _register_fact_structref, fact_mutability_protected_setattr, fact_lower_setattr, _fact_get_chr_mbrs_infos
from cre.fact import repr_list_attr, repr_fact_attr, FactProxy, Fact, UntypedFact, uint_to_inheritance_bytes
from cre.utils import cast, ptr_t, _get_member_offset,  _load_ptr, _obj_cast_codegen, encode_idrec
import cloudpickle
from cre.obj import member_info_type, set_chr_mbrs




attr_offsets = np.array([0, 8, 16, 20],dtype=np.int16)
inheritance_bytes = tuple(list(uint_to_inheritance_bytes(13))) 
num_inh_bytes = len(inheritance_bytes)
hash_code = 'Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78'

@_register_fact_structref
class BaseFactClass(Fact):
    def __init__(self, fields, hash_code=None):
        super().__init__('BaseFact', fields, hash_code)
        self._fact_name = 'BaseFact'
        self.t_id = 13
        self._attr_offsets = attr_offsets
        self._hash_code = 'Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78'
        

    

field_list = cloudpickle.loads(b'\x80\x05\x95d\x01\x00\x00\x00\x00\x00\x00]\x94(\x8c\x05idrec\x94\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x18numba.core.types.scalars\x94\x8c\x07Integer\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x06uint64\x94\x8c\x08bitwidth\x94K@\x8c\x06signed\x94\x89\x8c\x05_code\x94K\x13u\x87\x94R\x94\x86\x94\x8c\x08hash_val\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x05int64\x94h\x12K@h\x13\x88h\x14K\x17u\x87\x94R\x94\x86\x94\x8c\x0cnum_chr_mbrs\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x06uint32\x94h\x12K h\x13\x89h\x14K\x12u\x87\x94R\x94\x86\x94\x8c\x15chr_mbrs_infos_offset\x94h$\x86\x94e.')
BaseFact = fact_type = BaseFactClass(field_list, hash_code)
BaseFact_w_mbr_infos = BaseFactClass(field_list+
[("chr_mbrs_infos", UniTuple(member_info_type,0)),
 ("num_inh_bytes", u1),
 ("inh_bytes", UniTuple(u1, num_inh_bytes))])




@njit(cache=True)
def get_chr_mbrs_infos():
    st = new(BaseFact)
    return _fact_get_chr_mbrs_infos(st)

chr_mbrs_infos = get_chr_mbrs_infos()
BaseFactClass._chr_mbrs_infos = chr_mbrs_infos

@njit(u1(BaseFact), cache=True)
def isa_BaseFact(fact):
    return True

BaseFactClass._isa = isa_BaseFact

@njit(cache=True)
def ctor():
    st = new(BaseFact_w_mbr_infos)
    fact_lower_setattr(st,'idrec',encode_idrec(13,0,u1(-1)))
    fact_lower_setattr(st,'hash_val',0)
    set_chr_mbrs(st, ())
    fact_lower_setattr(st,'num_inh_bytes', num_inh_bytes)
    fact_lower_setattr(st,'inh_bytes', inheritance_bytes)
    
    return cast(st, BaseFact)

# Put in a tuple so it doesn't get wrapped in a method
BaseFactClass._ctor = (ctor,)

@njit(cache=True)
def get_idrec(self):
    return self.idrec

@njit(cache=True)
def get_hash_val(self):
    return self.hash_val

@njit(cache=True)
def get_num_chr_mbrs(self):
    return self.num_chr_mbrs

@njit(cache=True)
def get_chr_mbrs_infos_offset(self):
    return self.chr_mbrs_infos_offset


@njit(types.void(BaseFact,field_list[0][1]), cache=True)
def set_idrec(self, val):
    fact_mutability_protected_setattr(self,'idrec',val)

@njit(types.void(BaseFact,field_list[1][1]), cache=True)
def set_hash_val(self, val):
    fact_mutability_protected_setattr(self,'hash_val',val)

@njit(types.void(BaseFact,field_list[2][1]), cache=True)
def set_num_chr_mbrs(self, val):
    fact_mutability_protected_setattr(self,'num_chr_mbrs',val)

@njit(types.void(BaseFact,field_list[3][1]), cache=True)
def set_chr_mbrs_infos_offset(self, val):
    fact_mutability_protected_setattr(self,'chr_mbrs_infos_offset',val)

        
class BaseFactProxy(FactProxy):
    __numba_ctor = ctor
    _fact_type = BaseFact
    _fact_type_class = BaseFactClass
    _fact_name = 'BaseFact'
    
    t_id = 13
    _attr_offsets = attr_offsets
    _chr_mbrs_infos = chr_mbrs_infos
    _isa = isa_BaseFact
    _code = BaseFact._code
    _hash_code = 'Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78'

    def __new__(cls, *args,**kwargs):
        return ctor(*args,**kwargs)

    def __repr__(self):
        return f'BaseFact()'

    def __str__(self):
        return self.__repr__()

    def as_dict(self, key_attr='idrec'):
        return {'type' : 'BaseFact', }


    idrec = property(get_idrec, set_idrec)
    hash_val = property(get_hash_val, set_hash_val)
    num_chr_mbrs = property(get_num_chr_mbrs, set_num_chr_mbrs)
    chr_mbrs_infos_offset = property(get_chr_mbrs_infos_offset, set_chr_mbrs_infos_offset)

# Overload 'BaseFact' as its own constructor
@type_callable(BaseFact)
def ssp_call(context):
    
    # Note to self this requires *args, see https://github.com/numba/numba/issues/7973
    def typer():    
        return BaseFact
    return typer

@overload(numba_typeref_ctor)
def overload_BaseFact(self, ):
    if(self.instance_type is not BaseFact): return
    def impl(self, ):
        return ctor()
    return impl

BaseFactClass._fact_type = BaseFact
BaseFactClass._fact_proxy = BaseFactProxy
BaseFactClass._proxy_class = BaseFactProxy

BaseFact._fact_type_class = BaseFactClass
BaseFact._fact_proxy = BaseFactProxy
BaseFact._proxy_class = BaseFactProxy


define_boxing(BaseFactClass,BaseFactProxy)






