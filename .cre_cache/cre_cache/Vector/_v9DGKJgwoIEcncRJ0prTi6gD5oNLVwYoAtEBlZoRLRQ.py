
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def Vector_get_head(self):
    return self.head

@njit(cache=True)
def Vector_get_data(self):
    return self.data

@structref.register
class VectorTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class Vector(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def head(self):
        return Vector_get_head(self)
    
    @property
    def data(self):
        return Vector_get_data(self)
    

structref.define_constructor(Vector, VectorTypeTemplate, ['head','data'])
define_boxing(VectorTypeTemplate, Vector)


