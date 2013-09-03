import unittest
import numpy as np
#import fixed_point_arith
from scipy.io import loadmat

from fixed_point.arith import ComplexFixedInt


# test for string construction: create random ints, convert to bitstring and then convert back
class test_fixed_point_arith(unittest.TestCase):
    def test_neg(self):
        pass
        #raise NotImplementedError

    def test_cmult_sysgen_bit_consistency(self):
        # load test data
        sysgen_test_data = loadmat('cmult_fixed_pt_test_data.mat')

        b_real_int  = np.int64(sysgen_test_data['b_real_int'].ravel())
        b_imag_int  = np.int64(sysgen_test_data['b_imag_int'].ravel())
        w_real_int  = np.int64(sysgen_test_data['w_real_int'].ravel())
        w_imag_int  = np.int64(sysgen_test_data['w_imag_int'].ravel())
        bw_real_int = np.int64(sysgen_test_data['bw_real_int'].ravel())
        bw_imag_int = np.int64(sysgen_test_data['bw_imag_int'].ravel())

        input_fractlength = float(sysgen_test_data['input_fractlength'][0,0])
        output_fractlength = float(sysgen_test_data['output_fractlength'][0,0])

        # Check that the integer products match MATLAB's output
        np.array_equal(bw_real_int, b_real_int*w_real_int - b_imag_int*w_imag_int)
        np.array_equal(bw_imag_int, b_real_int*w_imag_int + b_imag_int*w_real_int)

        N = len(b_real_int)
        for k in range(N):
            b_val = np.complex(b_real_int[k], b_imag_int[k])* 2**(-input_fractlength)
            w_val = np.complex(w_real_int[k], w_imag_int[k])* 2**(-input_fractlength)
            bw_val = np.complex(bw_real_int[k], bw_imag_int[k])* 2**(-output_fractlength)

            dtype = (0, input_fractlength)
            b = ComplexFixedInt(b_val, dtype=dtype)
            w = ComplexFixedInt(w_val, dtype=dtype)
            output_dtype = (1, output_fractlength)
            bw = ComplexFixedInt(bw_val, dtype=output_dtype)
            # print b*w
            self.assertTrue( (bw_imag_int[k] * 2**-output_fractlength) == float((b*w).imag) and (bw_real_int[k] * 2**-output_fractlength) == float((b*w).real) )

    def test_mul_scale_factor(self):
        a = fixed_point.FixedInt(0.75, dtype='A(1,7)')
        a * 2
        a * 4
        a * 2**20

if __name__ == '__main__':
    unittest.main()
