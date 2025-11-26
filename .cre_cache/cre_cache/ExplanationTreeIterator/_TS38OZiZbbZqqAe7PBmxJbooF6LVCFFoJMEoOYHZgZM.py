
from numba.core import types
from numba import njit
from cre.structref import CastFriendlyStructref, define_boxing
from numba.experimental import structref
@njit(cache=True)
def ExplanationTreeIterator_get_tree(self):
    return self.tree

@njit(cache=True)
def ExplanationTreeIterator_get_entry_ind(self):
    return self.entry_ind

@njit(cache=True)
def ExplanationTreeIterator_get_n_entries(self):
    return self.n_entries

@njit(cache=True)
def ExplanationTreeIterator_get_arg_iters(self):
    return self.arg_iters

@njit(cache=True)
def ExplanationTreeIterator_get_cached_func(self):
    return self.cached_func

@structref.register
class ExplanationTreeIteratorTypeTemplate(CastFriendlyStructref):
    pass
    # def preprocess_fields(self, fields):
    #     return tuple((name, types.unliteral(typ)) for name, typ in fields)

class ExplanationTreeIterator(structref.StructRefProxy):
    def __new__(cls, *args):
        return structref.StructRefProxy.__new__(cls, *args)

    @property
    def tree(self):
        return ExplanationTreeIterator_get_tree(self)
    
    @property
    def entry_ind(self):
        return ExplanationTreeIterator_get_entry_ind(self)
    
    @property
    def n_entries(self):
        return ExplanationTreeIterator_get_n_entries(self)
    
    @property
    def arg_iters(self):
        return ExplanationTreeIterator_get_arg_iters(self)
    
    @property
    def cached_func(self):
        return ExplanationTreeIterator_get_cached_func(self)
    

structref.define_constructor(ExplanationTreeIterator, ExplanationTreeIteratorTypeTemplate, ['tree','entry_ind','n_entries','arg_iters','cached_func'])
define_boxing(ExplanationTreeIteratorTypeTemplate, ExplanationTreeIterator)


