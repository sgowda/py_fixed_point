#!/usr/bin/python
"""
FFT functions for the fixed-point FFT
"""
import rounding
import arith

def opt_round(input, dtype, method):
    if dtype is not None:
        return rounding.round(input, dtype, method=method)
    else:
        return input
    
def mult(b, w, dtype=None, round_method='trunc'):
    bw = b * w
    return opt_round(bw, dtype, round_method)

def add(a, b, dtype=None, round_method='trunc'):
    sum = a + b
    return opt_round(sum, dtype, round_method)

def sub(a, b, dtype=None, round_method='trunc'):
    sum = a - b
    return opt_round(sum, dtype, round_method)

def butterfly_rad2(a_fp, b_fp, w_fp, output_dtype=None, shift=False):
    if output_dtype == None: 
        output_dtype = a_fp.dtype

    # all data should have the same type
    assert a_fp.dtype == b_fp.dtype

    mult_dtype = (b_fp.real.intWidth + 2, b_fp.real.fractWidth + 2)
    bw_unrounded = b_fp * w_fp
    bw = rounding.round(bw_unrounded, mult_dtype, verbose=False)

    add_dtype = (mult_dtype[0] + 1, mult_dtype[1])
    apbw_fp = bw + a_fp
    ambw_fp = -bw + a_fp

    # downshift
    if shift:
        apbw_fp *= 2**-shift
        ambw_fp *= 2**-shift

    # Final cast before output
    apbw_fp = rounding.round(apbw_fp, a_fp.real.dtype, 'trunc')
    ambw_fp = rounding.round(ambw_fp, a_fp.real.dtype, 'trunc')
    of = False
    return apbw_fp, ambw_fp, of
    

