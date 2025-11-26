
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def CorgiGraph_get_change_head(self):
    return self.change_head

@njit(cache=True)
def CorgiGraph_get_memset(self):
    return self.memset

@njit(cache=True)
def CorgiGraph_get_nodes_by_nargs(self):
    return self.nodes_by_nargs

@njit(cache=True)
def CorgiGraph_get_n_nodes(self):
    return self.n_nodes

@njit(cache=True)
def CorgiGraph_get_root_nodes(self):
    return self.root_nodes

@njit(cache=True)
def CorgiGraph_get_global_modify_map(self):
    return self.global_modify_map

@njit(cache=True)
def CorgiGraph_get_global_t_id_root_map(self):
    return self.global_t_id_root_map

@njit(cache=True)
def CorgiGraph_get_total_weight(self):
    return self.total_weight

@njit(cache=True)
def CorgiGraph_get_end_nodes(self):
    return self.end_nodes

@njit(cache=True)
def CorgiGraph_get_var_end_join_ptrs(self):
    return self.var_end_join_ptrs

@njit(cache=True)
def CorgiGraph_get_match_iter_prototype_inst(self):
    return self.match_iter_prototype_inst

@structref.register
class CorgiGraphTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class CorgiGraph(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def change_head(self):
        return CorgiGraph_get_change_head(self)
    
    @property
    def memset(self):
        return CorgiGraph_get_memset(self)
    
    @property
    def nodes_by_nargs(self):
        return CorgiGraph_get_nodes_by_nargs(self)
    
    @property
    def n_nodes(self):
        return CorgiGraph_get_n_nodes(self)
    
    @property
    def root_nodes(self):
        return CorgiGraph_get_root_nodes(self)
    
    @property
    def global_modify_map(self):
        return CorgiGraph_get_global_modify_map(self)
    
    @property
    def global_t_id_root_map(self):
        return CorgiGraph_get_global_t_id_root_map(self)
    
    @property
    def total_weight(self):
        return CorgiGraph_get_total_weight(self)
    
    @property
    def end_nodes(self):
        return CorgiGraph_get_end_nodes(self)
    
    @property
    def var_end_join_ptrs(self):
        return CorgiGraph_get_var_end_join_ptrs(self)
    
    @property
    def match_iter_prototype_inst(self):
        return CorgiGraph_get_match_iter_prototype_inst(self)
    


define_boxing(CorgiGraphTypeTemplate, CorgiGraph)


