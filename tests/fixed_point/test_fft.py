import unittest
import numpy as np
from scipy.io import loadmat

import fixed_point
from fixed_point.arith import FixedInt, ComplexFixedInt
from fixed_point.rounding import Cast

# TODO there appears to be an overflow that occurs here but not in XSG!
# (k = 4 in test data)

def get_matlab_complex_fi(var_name, data, suffix='_int'):
    """
    Reconstruct a complex array from saved matlab fixed-point data
    """
    real_int = np.int64(data['%s_real%s' % (var_name, suffix)].ravel())
    imag_int = np.int64(data['%s_imag%s' % (var_name, suffix)].ravel())
    return real_int + imag_int * 1j

# test for string construction: create random ints, convert to bitstring and then convert back
class test_fixed_point_fft(unittest.TestCase):
    def test_butterfly(self):
        xsg_test_data = loadmat('butterfly_rad2_fixed_pt_test_data.mat')
        input_bitwidth = float(xsg_test_data['input_bitwidth'][0,0])
        input_fractwidth = float(xsg_test_data['input_fractlength'][0,0])
        a = get_matlab_complex_fi('a', xsg_test_data)*2**-input_fractwidth
        b = get_matlab_complex_fi('b', xsg_test_data)*2**-input_fractwidth
        w = get_matlab_complex_fi('w', xsg_test_data)*2**-input_fractwidth

        apbw_flops = a + b*w
                                                                         
        of = xsg_test_data['of'].ravel().astype(bool)
        apbw = get_matlab_complex_fi('apbw', xsg_test_data)*2**-input_fractwidth
        ambw = get_matlab_complex_fi('ambw', xsg_test_data)*2**-input_fractwidth

        apbw_diff = apbw - apbw_flops

        apbw_real_int = xsg_test_data['apbw_real_int'].ravel()
        apbw_imag_int = xsg_test_data['apbw_imag_int'].ravel()

        N = len(of)
        for k in range(N):
            if of[k]:
                continue
            #print k
            a_fp = ComplexFixedInt(a[k], dtype=(0,17))
            b_fp = ComplexFixedInt(b[k], dtype=(0,17))
            w_fp = ComplexFixedInt(w[k], dtype=(0,17))

            apbw_fp, ambw_fp, of_k = fixed_point.fft.butterfly_rad2(a_fp, b_fp, 
                w_fp, None, shift=False)
            self.assertTrue(apbw_real_int[k] == apbw_fp.real.value)
            self.assertTrue(apbw_imag_int[k] == apbw_fp.imag.value)

if __name__ == '__main__':
    unittest.main()
