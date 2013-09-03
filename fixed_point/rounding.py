#!/usr/bin/python
"""
Library functions to round fixed-point integers
"""
from fixed_point.arith import FixedInt, ComplexFixedInt
import numpy as np

# TODO 
# rounding for complex ints

def round(input, output_dtype, method='trunc', verbose=False):
    if isinstance(input, ComplexFixedInt):
        real_rounded = round(input.real, output_dtype, method, verbose)
        imag_rounded = round(input.imag, output_dtype, method, verbose)
        return ComplexFixedInt.concat(real_rounded, imag_rounded)

    if method == 'trunc':
        return round_trunc(input, output_dtype, verbose=verbose)
    else:
        raise NotImplementedError("Unrecognized rounding method: %s" % method)

def round_trunc(input, output_dtype, verbose=False):
    input_intWidth, input_fractWidth = input.intWidth, input.fractWidth
    output_intWidth, output_fractWidth = output_dtype
    if input_intWidth == output_intWidth:
        bit_sel_start = None
    else:
        bit_sel_start = output_intWidth + input_fractWidth + 1
    bit_sel_end = input_fractWidth - output_fractWidth
    if verbose:
        print bit_sel_start, bit_sel_end
    bit_sel = slice(bit_sel_start, bit_sel_end, -1)
    return FixedInt.promote(input[bit_sel])

class Cast():
    def __init__(self, input_dtype, output_dtype, type='trunc'):
        self.output_dtype = output_dtype
        if type == 'trunc':
            self.rounding_method = self.round_trunc
        elif type == 'trunc':
            self.rounding_method = self.round_inf
        else:
            raise ValueError("Unknown type of rounding: %s" % type)

    def round_trunc(self, num):
        """Round a FixedInt using truncation"""
        pass

    def round_inf(self, num):
        """Round a FixedInt using rounding to infinity"""
        pass
        
    def __call__(self, num):
        if isinstance(num, FixedInt):
            return self.rounding_method(num)
        elif isinstance(num, ComplexFixedInt):
            real_rounded = self.rounding_method(num.real)
            imag_rounded = self.rounding_method(num.imag)
            return ComplexFixedInt.concat(real_rounded, imag_rounded)
        else:
            raise ValueError("Unknown input type: %s" % type(num))
