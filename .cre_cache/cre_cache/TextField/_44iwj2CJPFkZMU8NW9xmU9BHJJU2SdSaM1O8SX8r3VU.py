
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
from cre.fact import repr_list_attr, repr_fact_attr, FactProxy, Fact, UntypedFact, BaseFact, base_list_type, fact_to_ptr, get_inheritance_bytes_len_ptr, uint_to_inheritance_bytes
from cre.utils import cast, ptr_t, _get_member_offset,  _load_ptr, _obj_cast_codegen, encode_idrec
import cloudpickle
from cre.obj import member_info_type, set_chr_mbrs
from cre_cache.Component._ZfViAqlCAX477GZtVOdqOykfWIBJrYWINOFy90eu84E import Component as parent_type, inheritance_bytes as parent_inh_bytes



attr_offsets = np.array([0, 8, 16, 20, 24, 72, 80, 88, 96, 104, 120, 168],dtype=np.int16)
inheritance_bytes = tuple(list(parent_inh_bytes) + [u1(0)] + list(uint_to_inheritance_bytes(18))) 
num_inh_bytes = len(inheritance_bytes)
hash_code = '44iwj2CJPFkZMU8NW9xmU9BHJJU2SdSaM1O8SX8r3VU'

@_register_fact_structref
class TextFieldClass(Fact):
    def __init__(self, fields, hash_code=None):
        super().__init__('TextField', fields, hash_code)
        self._fact_name = 'TextField'
        self.t_id = 18
        self._attr_offsets = attr_offsets
        self._hash_code = '44iwj2CJPFkZMU8NW9xmU9BHJJU2SdSaM1O8SX8r3VU'
        

    

field_list = cloudpickle.loads(b'\x80\x05\x95\xe1\x04\x00\x00\x00\x00\x00\x00]\x94(\x8c\x05idrec\x94\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x18numba.core.types.scalars\x94\x8c\x07Integer\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x06uint64\x94\x8c\x08bitwidth\x94K@\x8c\x06signed\x94\x89\x8c\x05_code\x94K\x13u\x87\x94R\x94\x86\x94\x8c\x08hash_val\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x05int64\x94h\x12K@h\x13\x88h\x14K\x17u\x87\x94R\x94\x86\x94\x8c\x0cnum_chr_mbrs\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x06uint32\x94h\x12K h\x13\x89h\x14K\x12u\x87\x94R\x94\x86\x94\x8c\x15chr_mbrs_infos_offset\x94h$\x86\x94\x8c\x02id\x94h\x04h\x07\x8c\x15numba.core.types.misc\x94\x8c\x0bUnicodeType\x94\x93\x94h\rN\x87\x94}\x94(h\x10\x8c\x0cunicode_type\x94h\x14K\x08u\x87\x94R\x94\x86\x94\x8c\x05above\x94h\x04h\x07\x8c?cre_cache.BaseFact._Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78\x94\x8c\rBaseFactClass\x94\x93\x94h\rN\x87\x94}\x94(\x8c\x07_fields\x94(\x8c\x05idrec\x94h\x16\x86\x94\x8c\x08hash_val\x94h\x1d\x86\x94\x8c\x0cnum_chr_mbrs\x94h$\x86\x94\x8c\x15chr_mbrs_infos_offset\x94h$\x86\x94t\x94\x8c\t_typename\x94h4h\x10\x8c4BaseFact_Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78\x94\x8c\n_fact_name\x94\x8c\x08BaseFact\x94\x8c\x04t_id\x94K\r\x8c\r_attr_offsets\x94\x8c\x12numpy.core.numeric\x94\x8c\x0b_frombuffer\x94\x93\x94(\x96\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x10\x00\x14\x00\x94\x8c\x05numpy\x94\x8c\x05dtype\x94\x93\x94\x8c\x02i2\x94\x89\x88\x87\x94R\x94(K\x03\x8c\x01<\x94NNNJ\xff\xff\xff\xffJ\xff\xff\xff\xffK\x00t\x94bK\x04\x85\x94\x8c\x01C\x94t\x94R\x94\x8c\n_hash_code\x94\x8c+Ps7sg8ORHv4NB4IjStkJiANLjEyjYARoWQkKVeOfs78\x94\x8c\x10_fact_type_class\x94h5\x8c\x0b_fact_proxy\x94h3\x8c\rBaseFactProxy\x94\x93\x94\x8c\x0c_proxy_class\x94h]u\x87\x94R\x94\x86\x94\x8c\x05below\x94h`\x86\x94\x8c\x04left\x94h`\x86\x94\x8c\x05right\x94h`\x86\x94\x8c\x07parents\x94h\x04h\x07\x8c\x1bnumba.core.types.containers\x94\x8c\x08ListType\x94\x93\x94h\rN\x87\x94}\x94(\x8c\titem_type\x94h`\x8c\x05dtype\x94h`h\x10\x8c\x1dListType[BaseFact_Ps7sg8ORHv]\x94h\x14Mq\x0bu\x87\x94R\x94\x86\x94\x8c\x05value\x94h0\x86\x94\x8c\x06locked\x94h\x04h\x07h\x08\x8c\x07Boolean\x94\x93\x94h\rN\x87\x94}\x94(h\x10\x8c\x04bool\x94h\x14K\x0fu\x87\x94R\x94\x86\x94e.')
TextField = fact_type = TextFieldClass(field_list, hash_code)
TextField_w_mbr_infos = TextFieldClass(field_list+
[("chr_mbrs_infos", UniTuple(member_info_type,8)),
 ("num_inh_bytes", u1),
 ("inh_bytes", UniTuple(u1, num_inh_bytes))])


TextField.parent_type = parent_type
pt = parent_type
while(pt is not None):
    @lower_cast(TextField, pt)
    def upcast(context, builder, fromty, toty, val):
        return _obj_cast_codegen(context, builder, val, fromty, toty,incref=False)                        
    pt = getattr(pt, 'parent_type', None)


@njit(cache=True)
def get_chr_mbrs_infos():
    st = new(TextField)
    return _fact_get_chr_mbrs_infos(st)

chr_mbrs_infos = get_chr_mbrs_infos()
TextFieldClass._chr_mbrs_infos = chr_mbrs_infos

#locals={'inheritance_bytes':Tuple((u1,num_inh_bytes))}
@njit(u1(BaseFact), cache=True)
def isa_TextField(fact):
    l, p = get_inheritance_bytes_len_ptr(fact)
    if(l >= num_inh_bytes):
        for i,b in enumerate(literal_unroll(inheritance_bytes)):
            f_b = _load_ptr(u1, p+i)
            if(b != f_b):
                return False
        return True
    else:
        return False

TextFieldClass._isa = isa_TextField

@njit(cache=True)
def ctor(id='',above=None,below=None,left=None,right=None,parents=None,value='',locked=False):
    st = new(TextField_w_mbr_infos)
    fact_lower_setattr(st,'idrec',encode_idrec(18,0,u1(-1)))
    fact_lower_setattr(st,'hash_val',0)
    set_chr_mbrs(st, ('id', 'above', 'below', 'left', 'right', 'parents', 'value', 'locked'))
    fact_lower_setattr(st,'num_inh_bytes', num_inh_bytes)
    fact_lower_setattr(st,'inh_bytes', inheritance_bytes)
    fact_lower_setattr(st,'id',id)
    fact_lower_setattr(st,'above',above)
    fact_lower_setattr(st,'below',below)
    fact_lower_setattr(st,'left',left)
    fact_lower_setattr(st,'right',right)
    fact_lower_setattr(st,'parents',parents)
    fact_lower_setattr(st,'value',value)
    fact_lower_setattr(st,'locked',locked)
    return cast(st, TextField)

# Put in a tuple so it doesn't get wrapped in a method
TextFieldClass._ctor = (ctor,)

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

@njit(cache=True)
def get_id(self):
    return self.id

@njit(cache=True)
def get_above_as_ptr(self):
    return get_fact_attr_ptr(self, 'above')

@njit(cache=True)
def get_above(self):
    return self.above

@njit(cache=True)
def get_below_as_ptr(self):
    return get_fact_attr_ptr(self, 'below')

@njit(cache=True)
def get_below(self):
    return self.below

@njit(cache=True)
def get_left_as_ptr(self):
    return get_fact_attr_ptr(self, 'left')

@njit(cache=True)
def get_left(self):
    return self.left

@njit(cache=True)
def get_right_as_ptr(self):
    return get_fact_attr_ptr(self, 'right')

@njit(cache=True)
def get_right(self):
    return self.right

@njit(cache=True)
def get_parents(self):
    return self.parents

@njit(cache=True)
def get_value(self):
    return self.value

@njit(cache=True)
def get_locked(self):
    return self.locked


@njit(types.void(TextField,field_list[0][1]), cache=True)
def set_idrec(self, val):
    fact_mutability_protected_setattr(self,'idrec',val)

@njit(types.void(TextField,field_list[1][1]), cache=True)
def set_hash_val(self, val):
    fact_mutability_protected_setattr(self,'hash_val',val)

@njit(types.void(TextField,field_list[2][1]), cache=True)
def set_num_chr_mbrs(self, val):
    fact_mutability_protected_setattr(self,'num_chr_mbrs',val)

@njit(types.void(TextField,field_list[3][1]), cache=True)
def set_chr_mbrs_infos_offset(self, val):
    fact_mutability_protected_setattr(self,'chr_mbrs_infos_offset',val)

@njit(types.void(TextField,field_list[4][1]), cache=True)
def set_id(self, val):
    fact_mutability_protected_setattr(self,'id',val)

@njit(types.void(TextField,field_list[5][1]), cache=True)
def set_above(self, val):
    fact_mutability_protected_setattr(self,'above',val)

@njit(types.void(TextField,field_list[6][1]), cache=True)
def set_below(self, val):
    fact_mutability_protected_setattr(self,'below',val)

@njit(types.void(TextField,field_list[7][1]), cache=True)
def set_left(self, val):
    fact_mutability_protected_setattr(self,'left',val)

@njit(types.void(TextField,field_list[8][1]), cache=True)
def set_right(self, val):
    fact_mutability_protected_setattr(self,'right',val)

@njit(types.void(TextField,field_list[9][1]), cache=True)
def set_parents(self, val):
    fact_mutability_protected_setattr(self,'parents',val)

@njit(types.void(TextField,field_list[10][1]), cache=True)
def set_value(self, val):
    fact_mutability_protected_setattr(self,'value',val)

@njit(types.void(TextField,field_list[11][1]), cache=True)
def set_locked(self, val):
    fact_mutability_protected_setattr(self,'locked',val)

        
class TextFieldProxy(FactProxy):
    __numba_ctor = ctor
    _fact_type = TextField
    _fact_type_class = TextFieldClass
    _fact_name = 'TextField'
    
    t_id = 18
    _attr_offsets = attr_offsets
    _chr_mbrs_infos = chr_mbrs_infos
    _isa = isa_TextField
    _code = TextField._code
    _hash_code = '44iwj2CJPFkZMU8NW9xmU9BHJJU2SdSaM1O8SX8r3VU'

    def __new__(cls, *args,**kwargs):
        return ctor(*args,**kwargs)

    def __repr__(self):
        return f'TextField(id={repr(self.id)}, above={repr_fact_attr(self.above)}, below={repr_fact_attr(self.below)}, left={repr_fact_attr(self.left)}, right={repr_fact_attr(self.right)}, parents={repr_list_attr(self.parents, "BaseFact")}, value={repr(self.value)}, locked={repr(self.locked)})'

    def __str__(self):
        return self.__repr__()

    def as_dict(self, key_attr='idrec'):
        return {'type' : 'TextField', 'id':get_id(self), 'above':getattr(get_above(self), key_attr, None), 'below':getattr(get_below(self), key_attr, None), 'left':getattr(get_left(self), key_attr, None), 'right':getattr(get_right(self), key_attr, None), 'parents':[getattr(x, key_attr, None) for x in get_parents(self)], 'value':get_value(self), 'locked':get_locked(self)}


    idrec = property(get_idrec, set_idrec)
    hash_val = property(get_hash_val, set_hash_val)
    num_chr_mbrs = property(get_num_chr_mbrs, set_num_chr_mbrs)
    chr_mbrs_infos_offset = property(get_chr_mbrs_infos_offset, set_chr_mbrs_infos_offset)
    id = property(get_id, set_id)
    above = property(get_above, set_above)
    below = property(get_below, set_below)
    left = property(get_left, set_left)
    right = property(get_right, set_right)
    parents = property(get_parents, set_parents)
    value = property(get_value, set_value)
    locked = property(get_locked, set_locked)

# Overload 'TextField' as its own constructor
@type_callable(TextField)
def ssp_call(context):
    
    # Note to self this requires *args, see https://github.com/numba/numba/issues/7973
    def typer(id,above,below,left,right,parents,value,locked):    
        return TextField
    return typer

@overload(numba_typeref_ctor)
def overload_TextField(self, id='',above=None,below=None,left=None,right=None,parents=None,value='',locked=False):
    if(self.instance_type is not TextField): return
    def impl(self, id='',above=None,below=None,left=None,right=None,parents=None,value='',locked=False):
        return ctor(id,above,below,left,right,parents,value,locked)
    return impl

TextFieldClass._fact_type = TextField
TextFieldClass._fact_proxy = TextFieldProxy
TextFieldClass._proxy_class = TextFieldProxy

TextField._fact_type_class = TextFieldClass
TextField._fact_proxy = TextFieldProxy
TextField._proxy_class = TextFieldProxy


define_boxing(TextFieldClass,TextFieldProxy)



from cre.var import VarType, var_ctor
# @njit(VarType(unicode_type), cache=True)
# def as_var(alias):
#     return var_ctor(TextField, 18, alias)
# TextField._as_var = as_var



