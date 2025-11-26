
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def ExplanationTreeEntry_get_is_func(self):
    return self.is_func

@njit(cache=True)
def ExplanationTreeEntry_get_is_const(self):
    return self.is_const

@njit(cache=True)
def ExplanationTreeEntry_get_func(self):
    return self.func

@njit(cache=True)
def ExplanationTreeEntry_get_var(self):
    return self.var

@njit(cache=True)
def ExplanationTreeEntry_get_child_arg_ptrs(self):
    return self.child_arg_ptrs

@structref.register
class ExplanationTreeEntryTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class ExplanationTreeEntry(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def is_func(self):
        return ExplanationTreeEntry_get_is_func(self)
    
    @property
    def is_const(self):
        return ExplanationTreeEntry_get_is_const(self)
    
    @property
    def func(self):
        return ExplanationTreeEntry_get_func(self)
    
    @property
    def var(self):
        return ExplanationTreeEntry_get_var(self)
    
    @property
    def child_arg_ptrs(self):
        return ExplanationTreeEntry_get_child_arg_ptrs(self)
    


define_boxing(ExplanationTreeEntryTypeTemplate, ExplanationTreeEntry)


