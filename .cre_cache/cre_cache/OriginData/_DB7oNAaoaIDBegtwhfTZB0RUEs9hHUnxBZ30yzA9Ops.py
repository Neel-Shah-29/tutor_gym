
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def OriginData_get_ptr(self):
    return self.ptr

@njit(cache=True)
def OriginData_get_name(self):
    return self.name

@njit(cache=True)
def OriginData_get_expr_template(self):
    return self.expr_template

@njit(cache=True)
def OriginData_get_shorthand_template(self):
    return self.shorthand_template

@njit(cache=True)
def OriginData_get_repr_const_addrs(self):
    return self.repr_const_addrs

@structref.register
class OriginDataTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class OriginData(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def ptr(self):
        return OriginData_get_ptr(self)
    
    @property
    def name(self):
        return OriginData_get_name(self)
    
    @property
    def expr_template(self):
        return OriginData_get_expr_template(self)
    
    @property
    def shorthand_template(self):
        return OriginData_get_shorthand_template(self)
    
    @property
    def repr_const_addrs(self):
        return OriginData_get_repr_const_addrs(self)
    

structref.define_constructor(OriginData, OriginDataTypeTemplate, ['ptr','name','expr_template','shorthand_template','repr_const_addrs'])
define_boxing(OriginDataTypeTemplate, OriginData)


