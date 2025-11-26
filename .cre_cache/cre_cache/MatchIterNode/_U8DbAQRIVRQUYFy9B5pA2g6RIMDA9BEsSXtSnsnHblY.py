
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def MatchIterNode_get_node(self):
    return self.node

@njit(cache=True)
def MatchIterNode_get_associated_arg_ind(self):
    return self.associated_arg_ind

@njit(cache=True)
def MatchIterNode_get_var_ind(self):
    return self.var_ind

@njit(cache=True)
def MatchIterNode_get_m_node_ind(self):
    return self.m_node_ind

@njit(cache=True)
def MatchIterNode_get_curr_ind(self):
    return self.curr_ind

@njit(cache=True)
def MatchIterNode_get_idrecs(self):
    return self.idrecs

@njit(cache=True)
def MatchIterNode_get_other_idrecs(self):
    return self.other_idrecs

@njit(cache=True)
def MatchIterNode_get_dep_m_node_inds(self):
    return self.dep_m_node_inds

@njit(cache=True)
def MatchIterNode_get_dep_node_ptrs(self):
    return self.dep_node_ptrs

@njit(cache=True)
def MatchIterNode_get_dep_arg_inds(self):
    return self.dep_arg_inds

@structref.register
class MatchIterNodeTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class MatchIterNode(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def node(self):
        return MatchIterNode_get_node(self)
    
    @property
    def associated_arg_ind(self):
        return MatchIterNode_get_associated_arg_ind(self)
    
    @property
    def var_ind(self):
        return MatchIterNode_get_var_ind(self)
    
    @property
    def m_node_ind(self):
        return MatchIterNode_get_m_node_ind(self)
    
    @property
    def curr_ind(self):
        return MatchIterNode_get_curr_ind(self)
    
    @property
    def idrecs(self):
        return MatchIterNode_get_idrecs(self)
    
    @property
    def other_idrecs(self):
        return MatchIterNode_get_other_idrecs(self)
    
    @property
    def dep_m_node_inds(self):
        return MatchIterNode_get_dep_m_node_inds(self)
    
    @property
    def dep_node_ptrs(self):
        return MatchIterNode_get_dep_node_ptrs(self)
    
    @property
    def dep_arg_inds(self):
        return MatchIterNode_get_dep_arg_inds(self)
    


define_boxing(MatchIterNodeTypeTemplate, MatchIterNode)


