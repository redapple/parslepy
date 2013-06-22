# borrowed from python-github2/tests/test_request.py
try:
    from nose.tools import assert_dict_equal
except ImportError:  # for Python < 2.7
    try:
        import unittest2
        _binding = unittest2.TestCase('run')
        assert_dict_equal = _binding.assertDictEqual
        assert_is_instance = _binding.assertIsInstance
        assert_tuple_equal = _binding.assertTupleEqual
    except:
        raise
