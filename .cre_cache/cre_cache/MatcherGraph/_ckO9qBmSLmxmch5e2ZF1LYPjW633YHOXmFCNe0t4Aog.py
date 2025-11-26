
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def MatcherGraph_get_change_head(self):
    return self.change_head

@njit(cache=True)
def MatcherGraph_get_memset(self):
    return self.memset

@njit(cache=True)
def MatcherGraph_get_nodes_by_nargs(self):
    return self.nodes_by_nargs

@njit(cache=True)
def MatcherGraph_get_n_nodes(self):
    return self.n_nodes

@njit(cache=True)
def MatcherGraph_get_root_nodes(self):
    return self.root_nodes

@njit(cache=True)
def MatcherGraph_get_global_modify_map(self):
    return self.global_modify_map

@njit(cache=True)
def MatcherGraph_get_global_t_id_root_map(self):
    return self.global_t_id_root_map

@njit(cache=True)
def MatcherGraph_get_total_weight(self):
    return self.total_weight

@structref.register
class MatcherGraphTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class MatcherGraph(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def change_head(self):
        return MatcherGraph_get_change_head(self)
    
    @property
    def memset(self):
        return MatcherGraph_get_memset(self)
    
    @property
    def nodes_by_nargs(self):
        return MatcherGraph_get_nodes_by_nargs(self)
    
    @property
    def n_nodes(self):
        return MatcherGraph_get_n_nodes(self)
    
    @property
    def root_nodes(self):
        return MatcherGraph_get_root_nodes(self)
    
    @property
    def global_modify_map(self):
        return MatcherGraph_get_global_modify_map(self)
    
    @property
    def global_t_id_root_map(self):
        return MatcherGraph_get_global_t_id_root_map(self)
    
    @property
    def total_weight(self):
        return MatcherGraph_get_total_weight(self)
    


define_boxing(MatcherGraphTypeTemplate, MatcherGraph)


