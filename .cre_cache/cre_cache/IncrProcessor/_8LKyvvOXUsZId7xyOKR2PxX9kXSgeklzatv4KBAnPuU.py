
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def IncrProcessor_get_in_memset(self):
    return self.in_memset

@njit(cache=True)
def IncrProcessor_get_change_queue_head(self):
    return self.change_queue_head

@structref.register
class IncrProcessorTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class IncrProcessor(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def in_memset(self):
        return IncrProcessor_get_in_memset(self)
    
    @property
    def change_queue_head(self):
        return IncrProcessor_get_change_queue_head(self)
    

structref.define_constructor(IncrProcessor, IncrProcessorTypeTemplate, ['in_memset','change_queue_head'])
define_boxing(IncrProcessorTypeTemplate, IncrProcessor)


