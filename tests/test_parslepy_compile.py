import parslepy
from parslepy.base import InvalidKeySyntax
from nose.tools import *
from lxml.etree import XPathSyntaxError

class TestKeySyntax(object):

    with_valid_keys = (
        ('title_big', ('title_big', None, None, None)),
        ('title-short(.span)', ('title-short', None, '(.span)', '.span')),
        ('title__2?', ('title__2', "?", None, None)),
        ('title_big?(#main)', ('title_big', "?", '(#main)', '#main')),
    )

    def test_key_regex(self):
        for key, target_results in self.with_valid_keys:
            yield self.compare_regex_results, key, target_results

    def compare_regex_results(self, key, results):
        m = parslepy.base.Parselet.REGEX_PARSELET_KEY.match(key)
        assert_true(m is not None)
        assert_tuple_equal(m.groups(), results)


    with_invalid_keys = (
        ({'title@(': 'h1'}, InvalidKeySyntax),

        ({'#test': 'h1'}, InvalidKeySyntax),
        ({'(#test)': 'h1'}, InvalidKeySyntax),
        ({'?(#test)': 'h1'}, InvalidKeySyntax),
        ({'.test': 'h1'}, InvalidKeySyntax),

        ({'test!': 'h1'}, InvalidKeySyntax),
        ({'test#': 'h1'}, InvalidKeySyntax),
        ({'test()': 'h1'}, InvalidKeySyntax),
        ({'?()': 'h1'}, InvalidKeySyntax),
        ({'test??': 'h1'}, InvalidKeySyntax),
        ({'test?()': 'h1'}, InvalidKeySyntax),
        ({'test~(test)': 'h1'}, InvalidKeySyntax),

        ({'test(!)': 'h1'}, XPathSyntaxError),
        ({'test(#)': 'h1'}, XPathSyntaxError),
        ({'test(.div ~)': 'h1'}, XPathSyntaxError),
    )

    def test_invalid_syntax(self):
        for parselet_dict, target_exception in self.with_invalid_keys:
            yield self.init_with_invalid_parselet_dict, parselet_dict, target_exception

    def init_with_invalid_parselet_dict(self, parselet_dict, target_exception):
        assert_raises(target_exception, parslepy.Parselet, parselet_dict)
