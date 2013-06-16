import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *

def dict_match(first, second):
    return not (set(first.items()) - set(second.items()))


def test_parslepy_init():
    parselet_script = {
        "title": "h1",
        "subtitle": "//h2"
    }
    parselet = parslepy.Parselet(parselet_script)

    assert_true(dict_match(parselet.parselet, parselet_script))

    assert_is_instance(parselet.parselet_tree, parslepy.base.ParsleyNode)
    assert_equal(len(parselet.parselet_tree), len(parselet_script), "not the same number of keys")

    for k,v in parselet.parselet_tree.items():
        assert_is_instance(k, parslepy.base.ParsleyContext)
        assert_is_instance(v, parslepy.base.Selector)


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
