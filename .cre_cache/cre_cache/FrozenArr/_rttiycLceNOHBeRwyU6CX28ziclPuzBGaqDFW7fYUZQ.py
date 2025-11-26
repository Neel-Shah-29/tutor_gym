
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def FrozenArr_get_arr(self):
    return self.arr

@structref.register
class FrozenArrTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class FrozenArr(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def arr(self):
        return FrozenArr_get_arr(self)
    

structref.define_constructor(FrozenArr, FrozenArrTypeTemplate, ['arr'])
define_boxing(FrozenArrTypeTemplate, FrozenArr)


