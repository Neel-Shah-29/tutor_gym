
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def CREContextData_get_name(self):
    return self.name

@njit(cache=True)
def CREContextData_get_unhandled_retro_registers(self):
    return self.unhandled_retro_registers

@njit(cache=True)
def CREContextData_get_fact_to_t_id(self):
    return self.fact_to_t_id

@njit(cache=True)
def CREContextData_get_t_id_to_type_names(self):
    return self.t_id_to_type_names

@njit(cache=True)
def CREContextData_get_parent_t_ids(self):
    return self.parent_t_ids

@njit(cache=True)
def CREContextData_get_child_t_ids(self):
    return self.child_t_ids

@njit(cache=True)
def CREContextData_get_attr_names(self):
    return self.attr_names

@structref.register
class CREContextDataTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class CREContextData(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def name(self):
        return CREContextData_get_name(self)
    
    @property
    def unhandled_retro_registers(self):
        return CREContextData_get_unhandled_retro_registers(self)
    
    @property
    def fact_to_t_id(self):
        return CREContextData_get_fact_to_t_id(self)
    
    @property
    def t_id_to_type_names(self):
        return CREContextData_get_t_id_to_type_names(self)
    
    @property
    def parent_t_ids(self):
        return CREContextData_get_parent_t_ids(self)
    
    @property
    def child_t_ids(self):
        return CREContextData_get_child_t_ids(self)
    
    @property
    def attr_names(self):
        return CREContextData_get_attr_names(self)
    


define_boxing(CREContextDataTypeTemplate, CREContextData)


