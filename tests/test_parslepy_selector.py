import parslepy
import parslepy.base
import parslepy.selectors
import lxml.cssselect
from nose.tools import *
from .tools import *


@raises(SyntaxError)
def test_parslepy_init_invalid_css_parselet():
    """Initialize Parselet() with invalid CSS selector"""
    parselet = parslepy.Parselet({ "title": "/h1[@]"})

@raises(SyntaxError)
def test_parslepy_init_invalid_xpath_parselet():
    """Initialize Parselet() with invalid XPath selector"""
    parselet = parslepy.Parselet({ "title": ".test .#."})

class TestDefaultSelectorHandlerSelectors(object):

    dsh = parslepy.base.DefaultSelectorHandler()

    selectors = (
        ("div.content", lxml.cssselect.CSSSelector),
        (".content #bogus span.first", lxml.cssselect.CSSSelector),
        ("div#main", lxml.cssselect.CSSSelector),
        ("div[@id='main']", lxml.etree.XPath),
        ('div[@id="main"]', lxml.etree.XPath),
        ("div", lxml.cssselect.CSSSelector),
        ("//div", lxml.etree.XPath),
        ("//a/@href", lxml.etree.XPath),
        ("img @src", lxml.etree.XPath),
        ("table tr[class='main']", lxml.cssselect.CSSSelector),
        ("tr[2]", lxml.etree.XPath),
    )

    def test_selector_class(self):
        for selector_string, target_class in self.selectors:
            yield self.compare_selector_class, selector_string, target_class

    def compare_selector_class(self, selector_string, target_class):
        s = self.dsh.make(selector_string)
        assert_is_instance(s, parslepy.selectors.Selector)
        assert_is_instance(
            s.selector, target_class,
            "%s compiled to '%s' and is not an instance of %s" % (selector_string, s.selector, target_class)
        )


class TestInvalidSelectors(object):

    dsh = parslepy.selectors.DefaultSelectorHandler()

    invalid_selectors = (
        '# ',
        '.#',
        '#t.',
        '#t-#',
        './//e',
        './/div class',
        './/div[@class="test]',
        'div[]',
        '.div[id@]',
        'div[@]',
        'span @',
        'span@',
        './/span//',
    )

    def test_invalid_css_selectors(self):
        for s in self.invalid_selectors:
            yield self.make_selector_expect_syntax_error, s

    @raises(SyntaxError)
    def make_selector_expect_syntax_error(self, s):
        self.dsh.make(s)
