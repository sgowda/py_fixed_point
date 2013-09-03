import unittest
import numpy as np
from scipy.io import loadmat

import fixed_point
from fixed_point.arith import FixedInt, ComplexFixedInt
from fixed_point.rounding import Cast

import pdb

# test for string construction: create random ints, convert to bitstring and then convert back
class test_fixed_point_arith(unittest.TestCase):
    def test_trunc(self):
        xsg_test_data = loadmat('rounding_behavior_Fix_8_7_to_Fix_5_4.mat')

        input_fractWidth = int(xsg_test_data['input_fract_len'][0,0])
        input_bit_width = int(xsg_test_data['input_bit_width'][0,0])
        input_intWidth = input_bit_width - input_fractWidth - 1
        input_dtype = (input_intWidth, input_fractWidth)

        output_fractWidth = int(xsg_test_data['output_fract_len'][0,0])
        output_bit_width = int(xsg_test_data['output_bit_width'][0,0])
        output_intWidth = output_bit_width - output_fractWidth - 1
        output_dtype = (output_intWidth, output_fractWidth)

        input_int = np.int64(xsg_test_data['input_int'].ravel())
        input_float = input_int * (2 ** -input_fractWidth);

        trunc_int = np.int64(xsg_test_data['trunc_int'].ravel())
        trunc_float = trunc_int * (2 ** -output_fractWidth)

        N = len(input_int)
        for k in range(N):
            input = FixedInt(input_float[k], dtype=input_dtype)
            input_trunc = fixed_point.rounding.round_trunc(input, output_dtype)

            self.assertTrue(input_trunc.fValue == trunc_float[k])
        
if __name__ == '__main__':
    unittest.main()
