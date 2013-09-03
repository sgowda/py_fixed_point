#!/usr/bin/python
"""
Real and complex fixed-point number objects
"""
import deModel
import numpy as np
from scipy.io import loadmat
import re


# TODO
# addition is not commutatitve
# negative int slicing is wrong
# be able to create ints from string that don't have a binary point (i.e. purely integer)



def bin(x, nbits=20, sep=False):
    """Print bitstring representation of integer with specified # of bits
    """
    if sep:
        nbits = int(np.ceil(float(nbits)/4)*4) # pad bitstr with 0s to make its length a multiple of 4
    bitstr = ''.join(x & (1 << i) and '1' or '0' for i in range(nbits-1,-1,-1)) 
    if sep:
        hex_len = nbits/4
        bitstr = ', '.join(bitstr[4*k:4*(k+1)] for k in range(hex_len))
    return bitstr

def insert_bin_pt(bitstr, fractWidth):
    if fractWidth > 0:
        return bitstr[:-fractWidth] + '.' + bitstr[-fractWidth:]
    else:
        return bitstr + '.'
    
    
BIN = {'0':0., '1':1., 'type':'b', 'base':2.0}
HEX = {'0':0, '1':1, '2':2, '3':2, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15, 'type':'x'}

def arb2dec(binstr, type='int', base_dict=BIN):
    """Convert string number of arbitrary base to decimal
    """
    base = base_dict['base']
    if type == 'int':
        return sum(base_dict[x]*base**k for k, x in enumerate(binstr[::-1]) )
    elif type == 'frac':
        return sum(base_dict[x]*base**(-k-1) for k, x in enumerate(binstr) ) 
    else:
        raise ValueError('bin2dec: type unknown: %s' % type)

class FixedInt(deModel.DeFixedInt):
    def __init__(self, fValue, dtype=None, **kwargs):
        # Get datatype of int
        if isinstance(dtype, str): # XSG format datatype specification
            if 'Fix' in dtype: 
                width = int(re.match('Fix_(\d+)_(\d+)', dtype).group(1))
                fractWidth = int(re.match('Fix_(\d+)_(\d+)', dtype).group(2))
                intWidth = width - fractWidth - 1
                self.dtype = intWidth, fractWidth
            elif 'UFix' in dtype: # XSG format unsigned int 
                raise NotImplementedError('Unsigned ints not verified yet!')
            else:
                intWidth = int(re.match('A\((\d+),\s*(\d+)\)', dtype).group(1))
                fractWidth = int(re.match('A\((\d+),\s*(\d+)\)', dtype).group(2))
                self.dtype = intWidth, fractWidth
        elif isinstance(dtype, tuple) and len(dtype) == 2: # deModel format
            self.dtype = dtype
            intWidth, fractWidth = dtype
        else:
            raise ValueError("Unrecognized data type: %s" % type(dtype))
        super(FixedInt, self).__init__(intWidth, fractWidth, float(fValue), **kwargs)
        self.inst_from_string = False

    @classmethod
    def from_str(cls, num, base_dict=BIN, **kwargs):
        """
        Parameters
        ----------
        num
         
        """
        base = base_dict['base']
        if not isinstance(num, str):
            raise ValueError("Must create object with string representation of number!")
        integ, frac = num.split('.') 

        if not np.all([bit in base_dict.keys() for bit in integ + frac]):
            raise ValueError("Not a valid binary integer!")

        # instantiate object
        intWidth = len(integ)
        fractWidth = len(frac)
        if integ[0] == '1': # remove sign extension
            while len(integ) > 1 and integ[0] == '1' and integ[1] == '1':
                integ = integ[1:]
            
        if integ == '':
            sign = 1
            sign_contrib = 0
        else:
            sign = (-1)**int(integ[0])
            intWidth -= 1
            sign_ext = integ[0] + '0'*len(integ[1:])
            sign_contrib = sign*arb2dec(sign_ext, type='int', base_dict=base_dict)

        int_contrib = sign_contrib + arb2dec(integ[1:], type='int', base_dict=base_dict)
        fValue = int_contrib + arb2dec(frac, type='frac', base_dict=base_dict)
        self = FixedInt(fValue, dtype=(intWidth, fractWidth), **kwargs)

        # store string represntations of integer and fractional parts of the number
        self.integ = integ
        self.frac = frac
        self.inst_from_string = True
        self.base_dict = base_dict
        return self

    def __int__(self):
        return self.value

    def __float__(self):
        return self.fValue

    def __repr__(self):
        return '%g, dtype=%s' % (float(self), self.rep)

    def __str__(self):
        return self.__repr__()

    def __neg__(self):
        """ 2's compliment negation: negate all the bits and add 1"""
        bitstr = self.bits()[2:]
        int_val = ~int(self) + 1
        bitstr = bin(~int(self)+1, nbits=self.width)
        bitstr = bitstr[:-self.fractWidth] + '.' + bitstr[-self.fractWidth:]
        return FixedInt.from_str(bitstr)

    @classmethod
    def promote(cls, obj):
        return FixedInt(obj.fValue, dtype=(obj.intWidth, obj.fractWidth))

    @classmethod
    def cast_more_bits(cls, num, dtype):
        return FixedInt(num.fValue, dtype=dtype)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int): # power of 2 multiplication -> shift
            shift_amt = np.ceil(np.log2(float(other)))
            pow_2 = 2**shift_amt == other
            min_scale = -(self.intWidth + 1)
            max_scale = self.fractWidth

            if pow_2 and shift_amt >= min_scale and shift_amt <= max_scale:
                if shift_amt > 0:
                    new_intWidth = self.intWidth + shift_amt
                    new_fractWidth = self.fractWidth - shift_amt
                elif shift_amt == 0:
                    return self
                elif shift_amt < 0:
                    new_intWidth = self.intWidth + shift_amt
                    new_fractWidth = self.fractWidth - shift_amt

                dtype = new_intWidth, new_fractWidth
                return FixedInt(self.fValue * 2**shift_amt, dtype=dtype)
            elif pow_2:
                raise ValueError("Scale factor is outside of valid range!")
            else:
                raise Exception("floating-fixed point multiplication not supported")
        else:
            m = super(FixedInt, self).__mul__(other)
            if m == NotImplemented:
                return NotImplemented
            else:
                return FixedInt.promote(m)

    def __rmul__(self, other):
        m = super(FixedInt, self).__mul__(other)
        return FixedInt.promote(m)

    def __add__(self, other):
        if isinstance(other, deModel.DeFixedInt):
            a = super(FixedInt, self).__add__(other)
            return FixedInt.promote(a)
        else:
            return NotImplemented
            
    def __sub__(self, other):
        if isinstance(other, deModel.DeFixedInt):
            a = super(FixedInt, self).__sub__(other)
            return FixedInt.promote(a)
        else:
            return NotImplemented

    def __getitem__(self, sl):
        bitstr_msb0 = self.bits(pretty=False)
        bitstr_lsb0 = bitstr_msb0[::-1]

        msb = sl.start
        lsb = sl.stop
        if msb is not None and lsb is not None:
            bitstr_sel_lsb0 = bitstr_lsb0[lsb:msb]
        elif msb == None and lsb == None:
            bitstr_sel_lsb0 = bitstr_lsb0
        elif msb == None:
            bitstr_sel_lsb0 = bitstr_lsb0[lsb:]
        elif lsb == None:
            bitstr_sel_lsb0 = bitstr_lsb0[:msb]
            
        bitstr_sel = bitstr_sel_lsb0[::-1]
        # insert new binary point
        bitstr_sel = insert_bin_pt(bitstr_sel, self.fractWidth - sl.stop)
        return FixedInt.from_str(bitstr_sel)

        #return FixedInt.promote(super(FixedInt, self).__getitem__(sl))

    def bits(self, pretty=True):
        bitstr = bin(int(self), nbits=int(self.width))
        if pretty:
            bitstr = '0b' + insert_bin_pt(bitstr, self.fractWidth) 
        return bitstr

    def reinterpret(self):
        pass

    def xsg_dtype(self):
        """
        Get the data type of this object in the Xilinx system generator
        notation
        """
        return "Fix_%d_%d" % (self.width, self.fractWidth)

    def repr_value(self):
        return self.value * 2**-self.fractWidth

    def scale(self, pow_2):
        """ Scale floating-point value by a power of 2 by shifting the 
        binary point
        """
        n_bits = self.intWidth + self.fractWidth
        new_fractWidth = self.fractWidth - pow_2
        new_intWidth = n_bits - new_fractWidth
        if new_fractWidth < 0 or new_intWidth < 0:
            raise Exception("Unsupported scale op")

        fValue = self.value * 2**-new_fractWidth
        return FixedInt(fValue, (new_intWidth, new_fractWidth))
        

class ComplexFixedInt():
    def __init__(self, cValue, dtype=None):
        #intWidth = int(intWidth)
        #fractWidth = int(fractWidth)
        #dtype = (intWidth, fractWidth)
        self.real = FixedInt(float(np.real(cValue)), dtype=dtype)
        self.imag = FixedInt(float(np.imag(cValue)), dtype=dtype)
        self.width = self.real.width
        self.dtype = self.real.dtype
        self.fValue = self.real.fValue + 1j*self.imag.fValue

    @classmethod
    def concat(cls, real, imag):
        if not real.rep == imag.rep:
            raise ValueError("Cannot concatenate real and imag components of different sizes")
        cValue = np.complex(real.fValue, imag.fValue)
        return ComplexFixedInt(cValue, dtype=(real.intWidth, real.fractWidth))

    def __mul__(self, other):
        # TODO some bit suppression will be required between products and sum
        if isinstance(other, FixedInt):
            prod_real = self.real * other
            prod_imag = self.imag * other
        elif isinstance(other, ComplexFixedInt):
            prod_real = self.real*other.real - self.imag*other.imag
            prod_imag = self.imag*other.real + self.real*other.imag
        else:
            raise ValueError("ComplexFixedInt: Unsupported type for mult")

        return ComplexFixedInt.concat(prod_real, prod_imag)

    def __add__(self, other):        
        if isinstance(other, FixedInt):
            sum_real = self.real + other
            sum_imag = FixedInt.cast_more_bits(self.imag, dtype=sum_real.rep)
        elif isinstance(other, ComplexFixedInt):
            sum_real = self.real + other.real
            sum_imag = self.imag + other.imag
        else:
            raise ValueError("ComplexFixedInt: Unsupported type for add: %s" % type(other))

        return ComplexFixedInt.concat(sum_real, sum_imag)

    def __radd__(self, other):
        return self.__add__(other)

    def conjugate(self):
        return ComplexFixedInt.concat(self.real, -self.imag)

    def real(self):
        return self.real

    def imag(self):
        return self.imag

    def __rmul__(self, other):
        return self.__mul__(other)

    def __pow__(self, power):
        """Calculate the absolute-value of the complex int"""
        if power == 2:
            return FixedInt.promote(self.real*self.real + self.imag*self.imag)
        elif power == 4:
            raise NotImplementedError

    def __neg__(self):
        return ComplexFixedInt.concat(-self.real, -self.imag)

    def __repr__(self):
        return '%g + %gj, dtype=%s' % (float(self.real), float(self.imag), self.real.rep)

    def repr_value(self):
        return self.real.repr_value() + 1j*self.imag.repr_value()

    def scale(self, pow_2):
        return ComplexFixedInt.concat(self.real.scale(pow_2), self.imag.scale(pow_2))
