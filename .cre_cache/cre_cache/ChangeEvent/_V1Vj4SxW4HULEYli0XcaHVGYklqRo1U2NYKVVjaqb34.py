
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def ChangeEvent_get_idrec(self):
    return self.idrec

@njit(cache=True)
def ChangeEvent_get_t_id(self):
    return self.t_id

@njit(cache=True)
def ChangeEvent_get_f_id(self):
    return self.f_id

@njit(cache=True)
def ChangeEvent_get_was_retracted(self):
    return self.was_retracted

@njit(cache=True)
def ChangeEvent_get_was_declared(self):
    return self.was_declared

@njit(cache=True)
def ChangeEvent_get_was_modified(self):
    return self.was_modified

@njit(cache=True)
def ChangeEvent_get_a_ids(self):
    return self.a_ids

@structref.register
class ChangeEventTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class ChangeEvent(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def idrec(self):
        return ChangeEvent_get_idrec(self)
    
    @property
    def t_id(self):
        return ChangeEvent_get_t_id(self)
    
    @property
    def f_id(self):
        return ChangeEvent_get_f_id(self)
    
    @property
    def was_retracted(self):
        return ChangeEvent_get_was_retracted(self)
    
    @property
    def was_declared(self):
        return ChangeEvent_get_was_declared(self)
    
    @property
    def was_modified(self):
        return ChangeEvent_get_was_modified(self)
    
    @property
    def a_ids(self):
        return ChangeEvent_get_a_ids(self)
    


define_boxing(ChangeEventTypeTemplate, ChangeEvent)


