import parslepy
import parslepy.base
import parslepy.selectors
import lxml.cssselect
from nose.tools import *
from .tools import *

class TestInvalidParseletInit(object):
    init_parselets = (
        #{ "title": ".test #"}, # this does not raise SyntaxError in lxml<3
        { "title": "/h1[@]"},
        { "title": "h1", "paragraphs": [".//p[@class,'news']"]},
    )
    def test_invalid_parselet_init(self):
        for parselet in self.init_parselets:
            yield self.init_parselet_expect_syntax_error, parselet

    @raises(SyntaxError)
    def init_parselet_expect_syntax_error(self, parselet):
        parslepy.Parselet(parselet)


class TestDefaultValidSelectors(object):

    dsh = parslepy.base.DefaultSelectorHandler()

    selectors = [
        ("div.content", lxml.etree.XPath),
        (".content #bogus span.first", lxml.etree.XPath),
        ("div#main", lxml.etree.XPath),
        ("div[@id='main']", lxml.etree.XPath),
        ('div[@id="main"]', lxml.etree.XPath),
        ("div", lxml.etree.XPath),
        ("//div", lxml.etree.XPath),
        ("//a/@href", lxml.etree.XPath),
        ("img @src", lxml.etree.XPath),
        ("table tr[class='main']", lxml.etree.XPath),
        ("tr[2]", lxml.etree.XPath),
    ]

    try:
        from cssselect.parser import FunctionalPseudoElement
        selectors.extend([
            ("img::attr(src)", lxml.etree.XPath),
        ])
    except:
        pass

    def test_selector_class(self):
        for selector_string, target_class in self.selectors:
            yield self.compare_selector_class, selector_string, target_class

    def compare_selector_class(self, selector_string, target_class):
        s = self.dsh.make(selector_string)
        assert_is_instance(s, parslepy.selectors.Selector)
        assert_is_instance(
            s.selector, target_class,
            "\n%s compiled to '%s' of type %s \n and is not an instance of %s" % (
                selector_string, s.selector, type(s.selector), target_class)
        )


class TestDefaultInvalidSelectors(object):

    dsh = parslepy.selectors.DefaultSelectorHandler()

    invalid_selectors = (
        # these does not raise SyntaxError in lxml<3
        #'# ',
        #'.#',
        #'#t-#',

        '#t.',
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


class TestXPathValidSelectors(object):

    xsh = parslepy.selectors.XPathSelectorHandler()

    selectors = (
        "div.content",
        "span[@id='main']",
        'header[@id="main"]',
        "div",
        "//div",
        "//a/@href",
        "img/@src",
        "./img/@src",
        ".//img/@alt",
        "table/tr[@class='main']",
        '//div[@id="main"]//tr[@class="item"]',
        "tr[2]",
    )

    def test_selector_class(self):
        for selector_string in self.selectors:
            yield self.compare_selector_class, selector_string

    def compare_selector_class(self, selector_string):
        s = self.xsh.make(selector_string)
        assert_is_instance(s, parslepy.selectors.Selector)
        assert_is_instance(
            s.selector, lxml.etree.XPath,
            "\n%s compiled to '%s' of type %s \n and is not an instance of %s" % (
                selector_string, s.selector, type(s.selector), lxml.etree.XPath)
        )


class TestXPathInvalidSelectors(object):

    xsh = parslepy.selectors.XPathSelectorHandler()

    invalid_selectors = (
        './//e',
        './/div class',
        './/div[@class="test]',
        'div[]',
        '.div[id@]',
        'div[@]',
        'span//',
        'span/@class/',
        './/span//',
    )

    def test_invalid_xpath_selectors(self):
        for s in self.invalid_selectors:
            yield self.make_selector_expect_syntax_error, s

    @raises(SyntaxError)
    def make_selector_expect_syntax_error(self, s):
        self.xsh.make(s)
