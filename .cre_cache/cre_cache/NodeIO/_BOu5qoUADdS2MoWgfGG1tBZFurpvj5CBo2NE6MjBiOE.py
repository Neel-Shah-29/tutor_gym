
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def NodeIO_get_is_root(self):
    return self.is_root

@njit(cache=True)
def NodeIO_get_change_buffer(self):
    return self.change_buffer

@njit(cache=True)
def NodeIO_get_change_inds(self):
    return self.change_inds

@njit(cache=True)
def NodeIO_get_remove_buffer(self):
    return self.remove_buffer

@njit(cache=True)
def NodeIO_get_remove_inds(self):
    return self.remove_inds

@njit(cache=True)
def NodeIO_get_match_idrecs_buffer(self):
    return self.match_idrecs_buffer

@njit(cache=True)
def NodeIO_get_match_idrecs(self):
    return self.match_idrecs

@njit(cache=True)
def NodeIO_get_match_inp_inds_buffer(self):
    return self.match_inp_inds_buffer

@njit(cache=True)
def NodeIO_get_match_inp_inds(self):
    return self.match_inp_inds

@njit(cache=True)
def NodeIO_get_idrecs_to_inds(self):
    return self.idrecs_to_inds

@njit(cache=True)
def NodeIO_get_match_holes(self):
    return self.match_holes

@njit(cache=True)
def NodeIO_get_width(self):
    return self.width

@njit(cache=True)
def NodeIO_get_parent_node_ptr(self):
    return self.parent_node_ptr

@structref.register
class NodeIOTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class NodeIO(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def is_root(self):
        return NodeIO_get_is_root(self)
    
    @property
    def change_buffer(self):
        return NodeIO_get_change_buffer(self)
    
    @property
    def change_inds(self):
        return NodeIO_get_change_inds(self)
    
    @property
    def remove_buffer(self):
        return NodeIO_get_remove_buffer(self)
    
    @property
    def remove_inds(self):
        return NodeIO_get_remove_inds(self)
    
    @property
    def match_idrecs_buffer(self):
        return NodeIO_get_match_idrecs_buffer(self)
    
    @property
    def match_idrecs(self):
        return NodeIO_get_match_idrecs(self)
    
    @property
    def match_inp_inds_buffer(self):
        return NodeIO_get_match_inp_inds_buffer(self)
    
    @property
    def match_inp_inds(self):
        return NodeIO_get_match_inp_inds(self)
    
    @property
    def idrecs_to_inds(self):
        return NodeIO_get_idrecs_to_inds(self)
    
    @property
    def match_holes(self):
        return NodeIO_get_match_holes(self)
    
    @property
    def width(self):
        return NodeIO_get_width(self)
    
    @property
    def parent_node_ptr(self):
        return NodeIO_get_parent_node_ptr(self)
    

structref.define_constructor(NodeIO, NodeIOTypeTemplate, ['is_root','change_buffer','change_inds','remove_buffer','remove_inds','match_idrecs_buffer','match_idrecs','match_inp_inds_buffer','match_inp_inds','idrecs_to_inds','match_holes','width','parent_node_ptr'])
define_boxing(NodeIOTypeTemplate, NodeIO)


