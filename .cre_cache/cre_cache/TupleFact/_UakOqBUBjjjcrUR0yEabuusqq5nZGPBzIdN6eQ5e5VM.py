from numba import njit, u1, u8, types
from numba.types import UniTuple
from numba.experimental.structref import new
from numba.extending import overload, lower_cast
from cre.fact import uint_to_inheritance_bytes
from cre.fact_intrinsics import define_boxing, get_fact_attr_ptr, _register_fact_structref, fact_mutability_protected_setattr, fact_lower_setattr, _fact_get_chr_mbrs_infos
from cre.tuple_fact import TupleFactClass, TupleFactProxy, tf_field_dict_from_types, tf_get_item, T_ID_TUPLE_FACT
from cre.utils import cast, encode_idrec, _get_member_offset
from cre.obj import member_info_type, set_chr_mbrs
import cloudpickle
TF_T_ID = T_ID_TUPLE_FACT#14
member_types = cloudpickle.loads(b'\x80\x05]\x94.')
n_members = len(member_types)
field_list = [(k,v) for k,v in tf_field_dict_from_types(member_types).items()]

inheritance_bytes = tuple(list(uint_to_inheritance_bytes(T_ID_TUPLE_FACT)) + [u1(0)] + list(uint_to_inheritance_bytes(14))) 
num_inh_bytes = len(inheritance_bytes)

@_register_fact_structref
class SpecializedTFClass(TupleFactClass):
    t_id = TF_T_ID
    def __str__(self):
        return 'TupleFact'

    __repr__ = __str__

SpecializedTF = fact_type = SpecializedTFClass(field_list)
SpecializedTF_w_mbr_infos = SpecializedTFClass(field_list+
[("chr_mbrs_infos", UniTuple(member_info_type,0)),
 ("num_inh_bytes", u1),
 ("inh_bytes", UniTuple(u1, num_inh_bytes))])



SpecializedTF._fact_name = "TupleFact"
SpecializedTF.t_id = TF_T_ID
# SpecializedTF._attr_offsets = attr_offsets
SpecializedTF._fact_type_class = SpecializedTFClass




default_idrec  = encode_idrec(TF_T_ID, 0, 0xFF)
@njit(cache=True)
def ctor():
    st = new(SpecializedTF_w_mbr_infos)
    fact_lower_setattr(st, 'idrec', default_idrec)
    fact_lower_setattr(st, 'hash_val', 0)
    set_chr_mbrs(st, ())
    fact_lower_setattr(st,'num_inh_bytes', num_inh_bytes)
    fact_lower_setattr(st,'inh_bytes', inheritance_bytes)
    
    return cast(st, SpecializedTF)

SpecializedTFClass._ctor = (ctor,)

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


@njit(types.void(SpecializedTF,field_list[0][1]), cache=True)
def set_idrec(self, val):
    fact_mutability_protected_setattr(self,'idrec',val)

@njit(types.void(SpecializedTF,field_list[1][1]), cache=True)
def set_hash_val(self, val):
    fact_mutability_protected_setattr(self,'hash_val',val)

@njit(types.void(SpecializedTF,field_list[2][1]), cache=True)
def set_num_chr_mbrs(self, val):
    fact_mutability_protected_setattr(self,'num_chr_mbrs',val)

@njit(types.void(SpecializedTF,field_list[3][1]), cache=True)
def set_chr_mbrs_infos_offset(self, val):
    fact_mutability_protected_setattr(self,'chr_mbrs_infos_offset',val)


class SpecializedTFProxy(TupleFactProxy):
    __numba_ctor = ctor
    _fact_type = SpecializedTF
    _fact_type_class = SpecializedTFClass
    t_id = TF_T_ID

    def __repr__(self):
        return f"TupleFact({', '.join([repr(tf_get_item(self,mt,i)) for i,mt in enumerate(member_types)])})"

    def __str__(self):
        return f"TF({', '.join([str(tf_get_item(self,mt,i)) for i,mt in enumerate(member_types)])})"

    def __getitem__(self, i):
        mt = member_types[i]
        return tf_get_item(self,mt,i)
    idrec = property(get_idrec, set_idrec)
    hash_val = property(get_hash_val, set_hash_val)
    num_chr_mbrs = property(get_num_chr_mbrs, set_num_chr_mbrs)
    chr_mbrs_infos_offset = property(get_chr_mbrs_infos_offset, set_chr_mbrs_infos_offset)

@overload(SpecializedTFProxy, prefer_literal=False)
def overload_tup_fact_ctor(*args):
    def impl(*args):
        return ctor(*args)
    return impl

SpecializedTF._fact_proxy = SpecializedTFProxy
SpecializedTF._proxy_class = SpecializedTFProxy

define_boxing(SpecializedTFClass,SpecializedTFProxy)

