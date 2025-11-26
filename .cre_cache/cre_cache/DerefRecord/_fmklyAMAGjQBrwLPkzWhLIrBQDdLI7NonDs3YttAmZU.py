
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def DerefRecord_get_parent_ptrs(self):
    return self.parent_ptrs

@njit(cache=True)
def DerefRecord_get_arg_ind(self):
    return self.arg_ind

@njit(cache=True)
def DerefRecord_get_base_idrec(self):
    return self.base_idrec

@njit(cache=True)
def DerefRecord_get_was_successful(self):
    return self.was_successful

@structref.register
class DerefRecordTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class DerefRecord(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def parent_ptrs(self):
        return DerefRecord_get_parent_ptrs(self)
    
    @property
    def arg_ind(self):
        return DerefRecord_get_arg_ind(self)
    
    @property
    def base_idrec(self):
        return DerefRecord_get_base_idrec(self)
    
    @property
    def was_successful(self):
        return DerefRecord_get_was_successful(self)
    

structref.define_constructor(DerefRecord, DerefRecordTypeTemplate, ['parent_ptrs','arg_ind','base_idrec','was_successful'])
define_boxing(DerefRecordTypeTemplate, DerefRecord)


