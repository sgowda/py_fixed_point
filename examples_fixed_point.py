#!/usr/bin/python
"""
Usage examples for FPGA
"""
import fixed_point
import numpy as np

## Instantiating a fixed-point int
#---------------------------------

# Instantiate a Fix_8_7 number, range = [-1, 1)
a = fixed_point.FixedInt(0.75, dtype='Fix_8_7')
print "a = "
print a

# The representation of numbers in deModel is slightly different from the 
# XSG conventions. HDL requires that signals be declared by their width, 
# and for convenience, XSG also allows you to specify whether the data is 
# signed or unsigned and where the binary point is. deModel fixed-point 
# integers instead specify the number of bits in the integer and the 
# fractional parts of the number. Furthermore, deModel assumes that the 
# sign bit is NOT included in the number of integer bits you specify. So a 
# Fix_8_7 number in XSG should be declared as a A(0,7) number, where we 
# specify 0 integer bits and 7 fractional bits. 
a = fixed_point.FixedInt(0.75, dtype='A(0,7)')

# or from the bitstring
# (bitstring instantiation is there if necessary, but it's not yet clear 
# if it's going to be useful)
a = fixed_point.FixedInt.from_str('.1100000')

# Viewing the binary representation
# ---------------------------------
a = fixed_point.FixedInt(0.75, dtype='A(0,7)')
print "Binary representation of a = "
print a.bits()

# Multiplication by scale factor results in a moving binary point
print "\nMultiplication by scale factor"
print "--------"
a = fixed_point.FixedInt(0.75, dtype='A(1,7)')
print "a = "
print a

print "a * 2**1"
print a * 2**1

print "a * 2**-1"
print a * 2**-1

# Instantiate a complex number
# ----------------------------
print "\nComplex number arithmetic"
print "--------"
b = fixed_point.ComplexFixedInt(0.5 + 0.75*1j, dtype='Fix_18_17')
print "b = "
print b

print "a * b = "
print a * b

print "b * a = "
print b * a

print "b ** 2 = "
print b ** 2

print "b*"
print np.conj(b)


print "\nAddition"
print "--------"
print "b + a = "
print b + a
print "a + b = "
print a + b
