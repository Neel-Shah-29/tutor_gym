
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
from cre_cache.gval._8AtJl452PpOfZ6bVXgyvMlCmXOUbVPpw5azqVCvGa9w import gval as parent_type, inheritance_bytes as parent_inh_bytes



attr_offsets = np.array([0, 8, 16, 20, 24, 32, 40, 48],dtype=np.int16)
inheritance_bytes = tuple(list(parent_inh_bytes) + [u1(0)] + list(uint_to_inheritance_bytes(26))) 
num_inh_bytes = len(inheritance_bytes)
hash_code = '0hOpPjHBijzMRr4bMVpDWyKgBdgPXuBBTRqZJGWpRl8'

@_register_fact_structref
class gval_boolClass(Fact):
    def __init__(self, fields, hash_code=None):
        super().__init__('gval_bool', fields, hash_code)
        self._fact_name = 'gval_bool'
        self.t_id = 26
        self._attr_offsets = attr_offsets
        self._hash_code = '0hOpPjHBijzMRr4bMVpDWyKgBdgPXuBBTRqZJGWpRl8'
        

    

field_list = cloudpickle.loads(b"\x80\x05\x95\xeb\x02\x00\x00\x00\x00\x00\x00]\x94(\x8c\x05idrec\x94\x8c\x19numba.core.types.abstract\x94\x8c\x13_type_reconstructor\x94\x93\x94\x8c\x07copyreg\x94\x8c\x0e_reconstructor\x94\x93\x94\x8c\x18numba.core.types.scalars\x94\x8c\x07Integer\x94\x93\x94\x8c\x08builtins\x94\x8c\x06object\x94\x93\x94N\x87\x94}\x94(\x8c\x04name\x94\x8c\x06uint64\x94\x8c\x08bitwidth\x94K@\x8c\x06signed\x94\x89\x8c\x05_code\x94K\x13u\x87\x94R\x94\x86\x94\x8c\x08hash_val\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x05int64\x94h\x12K@h\x13\x88h\x14K\x17u\x87\x94R\x94\x86\x94\x8c\x0cnum_chr_mbrs\x94h\x04h\x07h\nh\rN\x87\x94}\x94(h\x10\x8c\x06uint32\x94h\x12K h\x13\x89h\x14K\x12u\x87\x94R\x94\x86\x94\x8c\x15chr_mbrs_infos_offset\x94h$\x86\x94\x8c\x04head\x94h\x04h\x07\x8c\x07cre.obj\x94\x8c\x0fCREObjTypeClass\x94\x93\x94h\rN\x87\x94}\x94(\x8c\x07_fields\x94(h\x01h\x16\x86\x94h\x18h\x1d\x86\x94h\x1fh$\x86\x94h&h$\x86\x94t\x94\x8c\t_typename\x94h*h\x10\x8cznumba.CREObjTypeClass(('idrec', uint64), ('hash_val', int64), ('num_chr_mbrs', uint32), ('chr_mbrs_infos_offset', uint32))\x94h\x14M\xf5\n\x8c\x0c_proxy_class\x94h)\x8c\x0bCREObjProxy\x94\x93\x94u\x87\x94R\x94\x86\x94\x8c\x03flt\x94h\x04h\x07h\x08\x8c\x05Float\x94\x93\x94h\rN\x87\x94}\x94(h\x10\x8c\x07float64\x94h\x12K@h\x14K\x19u\x87\x94R\x94\x86\x94\x8c\x03nom\x94h\x16\x86\x94\x8c\x03val\x94h\x04h\x07h\x08\x8c\x07Boolean\x94\x93\x94h\rN\x87\x94}\x94(h\x10\x8c\x04bool\x94h\x14K\x0fu\x87\x94R\x94\x86\x94e.")
gval_bool = fact_type = gval_boolClass(field_list, hash_code)
gval_bool_w_mbr_infos = gval_boolClass(field_list+
[("chr_mbrs_infos", UniTuple(member_info_type,4)),
 ("num_inh_bytes", u1),
 ("inh_bytes", UniTuple(u1, num_inh_bytes))])


gval_bool.parent_type = parent_type
pt = parent_type
while(pt is not None):
    @lower_cast(gval_bool, pt)
    def upcast(context, builder, fromty, toty, val):
        return _obj_cast_codegen(context, builder, val, fromty, toty,incref=False)                        
    pt = getattr(pt, 'parent_type', None)


@njit(cache=True)
def get_chr_mbrs_infos():
    st = new(gval_bool)
    return _fact_get_chr_mbrs_infos(st)

chr_mbrs_infos = get_chr_mbrs_infos()
gval_boolClass._chr_mbrs_infos = chr_mbrs_infos

#locals={'inheritance_bytes':Tuple((u1,num_inh_bytes))}
@njit(u1(BaseFact), cache=True)
def isa_gval_bool(fact):
    l, p = get_inheritance_bytes_len_ptr(fact)
    if(l >= num_inh_bytes):
        for i,b in enumerate(literal_unroll(inheritance_bytes)):
            f_b = _load_ptr(u1, p+i)
            if(b != f_b):
                return False
        return True
    else:
        return False

gval_boolClass._isa = isa_gval_bool

@njit(cache=True)
def ctor(head=None,flt=0.0,nom=0,val=False):
    st = new(gval_bool_w_mbr_infos)
    fact_lower_setattr(st,'idrec',encode_idrec(26,0,u1(-1)))
    fact_lower_setattr(st,'hash_val',0)
    set_chr_mbrs(st, ('head', 'flt', 'nom', 'val'))
    fact_lower_setattr(st,'num_inh_bytes', num_inh_bytes)
    fact_lower_setattr(st,'inh_bytes', inheritance_bytes)
    fact_lower_setattr(st,'head',head)
    fact_lower_setattr(st,'flt',flt)
    fact_lower_setattr(st,'nom',nom)
    fact_lower_setattr(st,'val',val)
    return cast(st, gval_bool)

# Put in a tuple so it doesn't get wrapped in a method
gval_boolClass._ctor = (ctor,)

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
def get_head(self):
    return self.head

@njit(cache=True)
def get_flt(self):
    return self.flt

@njit(cache=True)
def get_nom(self):
    return self.nom

@njit(cache=True)
def get_val(self):
    return self.val


@njit(types.void(gval_bool,field_list[0][1]), cache=True)
def set_idrec(self, val):
    fact_mutability_protected_setattr(self,'idrec',val)

@njit(types.void(gval_bool,field_list[1][1]), cache=True)
def set_hash_val(self, val):
    fact_mutability_protected_setattr(self,'hash_val',val)

@njit(types.void(gval_bool,field_list[2][1]), cache=True)
def set_num_chr_mbrs(self, val):
    fact_mutability_protected_setattr(self,'num_chr_mbrs',val)

@njit(types.void(gval_bool,field_list[3][1]), cache=True)
def set_chr_mbrs_infos_offset(self, val):
    fact_mutability_protected_setattr(self,'chr_mbrs_infos_offset',val)

@njit(types.void(gval_bool,field_list[4][1]), cache=True)
def set_head(self, val):
    fact_mutability_protected_setattr(self,'head',val)

@njit(types.void(gval_bool,field_list[5][1]), cache=True)
def set_flt(self, val):
    fact_mutability_protected_setattr(self,'flt',val)

@njit(types.void(gval_bool,field_list[6][1]), cache=True)
def set_nom(self, val):
    fact_mutability_protected_setattr(self,'nom',val)

@njit(types.void(gval_bool,field_list[7][1]), cache=True)
def set_val(self, val):
    fact_mutability_protected_setattr(self,'val',val)

        
class gval_boolProxy(FactProxy):
    __numba_ctor = ctor
    _fact_type = gval_bool
    _fact_type_class = gval_boolClass
    _fact_name = 'gval_bool'
    
    t_id = 26
    _attr_offsets = attr_offsets
    _chr_mbrs_infos = chr_mbrs_infos
    _isa = isa_gval_bool
    _code = gval_bool._code
    _hash_code = '0hOpPjHBijzMRr4bMVpDWyKgBdgPXuBBTRqZJGWpRl8'

    def __new__(cls, *args,**kwargs):
        return ctor(*args,**kwargs)

    def __repr__(self):
        return f'gval_bool(head={repr(self.head)}, flt={repr(self.flt)}, nom={repr(self.nom)}, val={repr(self.val)})'

    def __str__(self):
        return self.__repr__()

    def as_dict(self, key_attr='idrec'):
        return {'type' : 'gval_bool', 'head':get_head(self), 'flt':get_flt(self), 'nom':get_nom(self), 'val':get_val(self)}


    idrec = property(get_idrec, set_idrec)
    hash_val = property(get_hash_val, set_hash_val)
    num_chr_mbrs = property(get_num_chr_mbrs, set_num_chr_mbrs)
    chr_mbrs_infos_offset = property(get_chr_mbrs_infos_offset, set_chr_mbrs_infos_offset)
    head = property(get_head, set_head)
    flt = property(get_flt, set_flt)
    nom = property(get_nom, set_nom)
    val = property(get_val, set_val)

# Overload 'gval_bool' as its own constructor
@type_callable(gval_bool)
def ssp_call(context):
    
    # Note to self this requires *args, see https://github.com/numba/numba/issues/7973
    def typer(head,flt,nom,val):    
        return gval_bool
    return typer

@overload(numba_typeref_ctor)
def overload_gval_bool(self, head=None,flt=0.0,nom=0,val=False):
    if(self.instance_type is not gval_bool): return
    def impl(self, head=None,flt=0.0,nom=0,val=False):
        return ctor(head,flt,nom,val)
    return impl

gval_boolClass._fact_type = gval_bool
gval_boolClass._fact_proxy = gval_boolProxy
gval_boolClass._proxy_class = gval_boolProxy

gval_bool._fact_type_class = gval_boolClass
gval_bool._fact_proxy = gval_boolProxy
gval_bool._proxy_class = gval_boolProxy


define_boxing(gval_boolClass,gval_boolProxy)



from cre.var import VarType, var_ctor
# @njit(VarType(unicode_type), cache=True)
# def as_var(alias):
#     return var_ctor(gval_bool, 26, alias)
# gval_bool._as_var = as_var



