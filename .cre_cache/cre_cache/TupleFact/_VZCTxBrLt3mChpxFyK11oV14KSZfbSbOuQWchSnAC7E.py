from numba import njit, u1, u8, types
from numba.types import UniTuple
from numba.experimental.structref import new
from numba.extending import overload, lower_cast
from cre.fact import uint_to_inheritance_bytes
from cre.fact_intrinsics import define_boxing, get_fact_attr_ptr, _register_fact_structref, fact_mutability_protected_setattr, fact_lower_setattr, _fact_get_chr_mbrs_infos
from cre.tuple_fact import TupleFactClass, TupleFactProxy, tf_field_dict_from_types, tf_get_item, T_ID_TUPLE_FACT, TupleFact
from cre.utils import cast, encode_idrec, _get_member_offset
from cre.obj import member_info_type, set_chr_mbrs
import cloudpickle
TF_T_ID = T_ID_TUPLE_FACT#30
member_types = cloudpickle.loads(b'\x80\x05\x95\xfe\x05\x00\x00\x00\x00\x00\x00]\x94(\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x0cunicode_type\x94\x8c\x05_code\x94K\x08u\x87\x94R\x94h\x03h\x06\x8c\x07cre.var\x94\x8c\x0cVarTypeClass\x94\x93\x94h\x0cN\x87\x94}\x94(\x8c\tbase_type\x94N\x8c\thead_type\x94N\x8c\x07_fields\x94(\x8c\x05idrec\x94h\x03h\x06\x8c\x18numba.core.types.scalars\x94\x8c\x07Integer\x94\x93\x94h\x0cN\x87\x94}\x94(h\x0f\x8c\x06uint64\x94\x8c\x08bitwidth\x94K@\x8c\x06signed\x94\x89h\x11K\x13u\x87\x94R\x94\x86\x94\x8c\x08hash_val\x94h\x03h\x06h\x1fh\x0cN\x87\x94}\x94(h\x0f\x8c\x05int64\x94h#K@h$\x88h\x11K\x17u\x87\x94R\x94\x86\x94\x8c\x0cnum_chr_mbrs\x94h\x03h\x06h\x1fh\x0cN\x87\x94}\x94(h\x0f\x8c\x06uint32\x94h#K h$\x89h\x11K\x12u\x87\x94R\x94\x86\x94\x8c\x15chr_mbrs_infos_offset\x94h4\x86\x94\x8c\x08base_ptr\x94h-\x86\x94\x8c\x0cbase_ptr_ref\x94h\x03h\x06\x8c\tcre.utils\x94\x8c\x03Ptr\x94\x93\x94h\x0cN\x87\x94}\x94(h\x0f\x8c\x05ptr_t\x94h#K@h$\x89h\x11M\x97\x02u\x87\x94R\x94\x86\x94\x8c\x08conj_ptr\x94h-\x86\x94\x8c\x06alias_\x94h\x13\x86\x94\x8c\x0fderef_attrs_str\x94h\x03h\x06h\x07\x8c\x08Optional\x94\x93\x94h\x0cN\x87\x94}\x94(\x8c\x04type\x94h\x13h\x0f\x8c\x1aOptionalType(unicode_type)\x94h\x11M\x0e\ru\x87\x94R\x94\x86\x94\x8c\x0bderef_infos\x94h\x03h\x06\x8c\x19numba.core.types.npytypes\x94\x8c\x05Array\x94\x93\x94h\x0cN\x87\x94}\x94(\x8c\x07aligned\x94\x89\x8c\x05dtype\x94h\x03h\x06hS\x8c\x06Record\x94\x93\x94h\x0cN\x87\x94}\x94(\x8c\x06fields\x94}\x94(hMhS\x8c\x0c_RecordField\x94\x93\x94(h\x03h\x06h\x1fh\x0cN\x87\x94}\x94(h\x0f\x8c\x05uint8\x94h#K\x08h$\x89h\x11K\x10u\x87\x94R\x94K\x00NNt\x94\x81\x94\x8c\x04a_id\x94ha(h4K\x01NNt\x94\x81\x94\x8c\x04t_id\x94ha(h\x03h\x06h\x1fh\x0cN\x87\x94}\x94(h\x0f\x8c\x06uint16\x94h#K\x10h$\x89h\x11K\x11u\x87\x94R\x94K\x05NNt\x94\x81\x94\x8c\x06offset\x94ha(h\x03h\x06h\x1fh\x0cN\x87\x94}\x94(h\x0f\x8c\x05int32\x94h#K h$\x88h\x11K\x16u\x87\x94R\x94K\x07NNt\x94\x81\x94u\x8c\x04size\x94K\x0bhX\x89h\x0f\x8c|Record(type[type=uint8;offset=0],a_id[type=uint32;offset=1],t_id[type=uint16;offset=5],offset[type=int32;offset=7];11;False)\x94h#KXh\x11M\x9e\x02u\x87\x94R\x94\x8c\x04ndim\x94K\x01\x8c\x06layout\x94\x8c\x01C\x94h\x0f\x8c\x94unaligned array(Record(type[type=uint8;offset=0],a_id[type=uint32;offset=1],t_id[type=uint16;offset=5],offset[type=int32;offset=7];11;False), 1d, C)\x94h\x11M\xc1\x0bu\x87\x94R\x94\x86\x94\x8c\tbase_t_id\x94hq\x86\x94\x8c\thead_t_id\x94hq\x86\x94\x8c\x06is_not\x94hf\x86\x94h\x19h\x03h\x06h\x07\x8c\x07Phantom\x94\x93\x94h\x0cN\x87\x94}\x94(h\x0f\x8c\x03any\x94h\x11K\x05u\x87\x94R\x94\x86\x94h\x1ah\x93\x86\x94t\x94\x8c\t_typename\x94h\x15h\x0f\x8c\x07VarType\x94h\x11M\x0f\ru\x87\x94R\x94e.')
n_members = len(member_types)
field_list = [(k,v) for k,v in tf_field_dict_from_types(member_types).items()]

inheritance_bytes = tuple(list(uint_to_inheritance_bytes(T_ID_TUPLE_FACT)) + [u1(0)] + list(uint_to_inheritance_bytes(30))) 
num_inh_bytes = len(inheritance_bytes)

@_register_fact_structref
class SpecializedTFClass(TupleFactClass):
    t_id = TF_T_ID
    def __str__(self):
        return 'TupleFact(unicode_type, VarType)'

    __repr__ = __str__

SpecializedTF = fact_type = SpecializedTFClass(field_list)
SpecializedTF_w_mbr_infos = SpecializedTFClass(field_list+
[("chr_mbrs_infos", UniTuple(member_info_type,2)),
 ("num_inh_bytes", u1),
 ("inh_bytes", UniTuple(u1, num_inh_bytes))])



SpecializedTF._fact_name = "TupleFact"
SpecializedTF.t_id = TF_T_ID
# SpecializedTF._attr_offsets = attr_offsets
SpecializedTF._fact_type_class = SpecializedTFClass
SpecializedTF._specialization_name = "TupleFact(unicode_type, VarType)"

SpecializedTF.parent_type = TupleFact
@lower_cast(SpecializedTF, TupleFact)
def upcast(context, builder, fromty, toty, val):
    return _obj_cast_codegen(context, builder, val, fromty, toty,incref=False)                        


default_idrec  = encode_idrec(TF_T_ID, 0, 0xFF)
@njit(cache=True)
def ctor(*members):
    st = new(SpecializedTF_w_mbr_infos)
    fact_lower_setattr(st, 'idrec', default_idrec)
    fact_lower_setattr(st, 'hash_val', 0)
    set_chr_mbrs(st, ('a0', 'a1'))
    fact_lower_setattr(st,'num_inh_bytes', num_inh_bytes)
    fact_lower_setattr(st,'inh_bytes', inheritance_bytes)
    fact_lower_setattr(st, 'a0', members[0])
    fact_lower_setattr(st, 'a1', members[1])
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

