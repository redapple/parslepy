import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *

def test_default_selector_handler():

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
    for selector_string, target_class in selectors:
        s = dsh.make(selector_string)
        assert_is_instance(s, parslepy.base.Selector)
        assert_is_instance(
            s.selector, target_class,
            "%s compiled to '%s' and is not an instance of %s" % (selector_string, s.selector, target_class)
        )
