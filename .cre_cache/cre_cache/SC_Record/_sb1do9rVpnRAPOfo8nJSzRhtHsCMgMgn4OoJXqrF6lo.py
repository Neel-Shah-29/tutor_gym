
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def SC_Record_get_data(self):
    return self.data

@njit(cache=True)
def SC_Record_get_stride(self):
    return self.stride

@njit(cache=True)
def SC_Record_get_is_func(self):
    return self.is_func

@njit(cache=True)
def SC_Record_get_is_const(self):
    return self.is_const

@njit(cache=True)
def SC_Record_get_func(self):
    return self.func

@njit(cache=True)
def SC_Record_get_n_args(self):
    return self.n_args

@njit(cache=True)
def SC_Record_get_var(self):
    return self.var

@njit(cache=True)
def SC_Record_get_depth(self):
    return self.depth

@structref.register
class SC_RecordTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class SC_Record(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def data(self):
        return SC_Record_get_data(self)
    
    @property
    def stride(self):
        return SC_Record_get_stride(self)
    
    @property
    def is_func(self):
        return SC_Record_get_is_func(self)
    
    @property
    def is_const(self):
        return SC_Record_get_is_const(self)
    
    @property
    def func(self):
        return SC_Record_get_func(self)
    
    @property
    def n_args(self):
        return SC_Record_get_n_args(self)
    
    @property
    def var(self):
        return SC_Record_get_var(self)
    
    @property
    def depth(self):
        return SC_Record_get_depth(self)
    


define_boxing(SC_RecordTypeTemplate, SC_Record)


