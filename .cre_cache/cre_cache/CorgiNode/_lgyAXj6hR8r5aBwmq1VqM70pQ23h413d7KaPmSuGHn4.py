
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def CorgiNode_get_memset_ptr(self):
    return self.memset_ptr

@njit(cache=True)
def CorgiNode_get_lit(self):
    return self.lit

@njit(cache=True)
def CorgiNode_get_op(self):
    return self.op

@njit(cache=True)
def CorgiNode_get_deref_depends(self):
    return self.deref_depends

@njit(cache=True)
def CorgiNode_get_n_vars(self):
    return self.n_vars

@njit(cache=True)
def CorgiNode_get_var_inds(self):
    return self.var_inds

@njit(cache=True)
def CorgiNode_get_t_ids(self):
    return self.t_ids

@njit(cache=True)
def CorgiNode_get_inp_widths(self):
    return self.inp_widths

@njit(cache=True)
def CorgiNode_get_head_ptr_buffers(self):
    return self.head_ptr_buffers

@njit(cache=True)
def CorgiNode_get_input_state_buffers(self):
    return self.input_state_buffers

@njit(cache=True)
def CorgiNode_get_inds_change_buffers(self):
    return self.inds_change_buffers

@njit(cache=True)
def CorgiNode_get_changed_inds(self):
    return self.changed_inds

@njit(cache=True)
def CorgiNode_get_unchanged_inds(self):
    return self.unchanged_inds

@njit(cache=True)
def CorgiNode_get_removed_inds(self):
    return self.removed_inds

@njit(cache=True)
def CorgiNode_get_inputs(self):
    return self.inputs

@njit(cache=True)
def CorgiNode_get_outputs(self):
    return self.outputs

@njit(cache=True)
def CorgiNode_get_truth_table(self):
    return self.truth_table

@njit(cache=True)
def CorgiNode_get_upstream_same_parents(self):
    return self.upstream_same_parents

@njit(cache=True)
def CorgiNode_get_upstream_aligned(self):
    return self.upstream_aligned

@njit(cache=True)
def CorgiNode_get_upstream_node_ptr(self):
    return self.upstream_node_ptr

@njit(cache=True)
def CorgiNode_get_modify_idrecs(self):
    return self.modify_idrecs

@structref.register
class CorgiNodeTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class CorgiNode(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def memset_ptr(self):
        return CorgiNode_get_memset_ptr(self)
    
    @property
    def lit(self):
        return CorgiNode_get_lit(self)
    
    @property
    def op(self):
        return CorgiNode_get_op(self)
    
    @property
    def deref_depends(self):
        return CorgiNode_get_deref_depends(self)
    
    @property
    def n_vars(self):
        return CorgiNode_get_n_vars(self)
    
    @property
    def var_inds(self):
        return CorgiNode_get_var_inds(self)
    
    @property
    def t_ids(self):
        return CorgiNode_get_t_ids(self)
    
    @property
    def inp_widths(self):
        return CorgiNode_get_inp_widths(self)
    
    @property
    def head_ptr_buffers(self):
        return CorgiNode_get_head_ptr_buffers(self)
    
    @property
    def input_state_buffers(self):
        return CorgiNode_get_input_state_buffers(self)
    
    @property
    def inds_change_buffers(self):
        return CorgiNode_get_inds_change_buffers(self)
    
    @property
    def changed_inds(self):
        return CorgiNode_get_changed_inds(self)
    
    @property
    def unchanged_inds(self):
        return CorgiNode_get_unchanged_inds(self)
    
    @property
    def removed_inds(self):
        return CorgiNode_get_removed_inds(self)
    
    @property
    def inputs(self):
        return CorgiNode_get_inputs(self)
    
    @property
    def outputs(self):
        return CorgiNode_get_outputs(self)
    
    @property
    def truth_table(self):
        return CorgiNode_get_truth_table(self)
    
    @property
    def upstream_same_parents(self):
        return CorgiNode_get_upstream_same_parents(self)
    
    @property
    def upstream_aligned(self):
        return CorgiNode_get_upstream_aligned(self)
    
    @property
    def upstream_node_ptr(self):
        return CorgiNode_get_upstream_node_ptr(self)
    
    @property
    def modify_idrecs(self):
        return CorgiNode_get_modify_idrecs(self)
    


define_boxing(CorgiNodeTypeTemplate, CorgiNode)


