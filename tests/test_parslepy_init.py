import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
from .tools import *

def test_parslepy_init_default():
    parselet_script = {
        "title": "h1",
        "subtitle": "//h2"
    }
    parselet = parslepy.Parselet(parselet_script)

    assert_dict_equal(parselet.parselet, parselet_script)

    assert_is_instance(parselet.parselet_tree, parslepy.base.ParsleyNode)
    assert_equal(len(parselet.parselet_tree), len(parselet_script), "not the same number of keys")

    for k,v in list(parselet.parselet_tree.items()):
        assert_is_instance(k, parslepy.base.ParsleyContext)
        assert_is_instance(v, parslepy.base.Selector)

    # since we did not provide a selector handler
    assert_is_instance(parselet.selector_handler, parslepy.base.DefaultSelectorHandler)

@raises(ValueError)
def test_parslepy_init_invalid_parselet():
    parselet = parslepy.Parselet("{ 'title': 'h1'}")

@raises(NotImplementedError)
def test_parslepy_init_selector_handler_error():
    parselet_script = {
        "title": "h1",
        "subtitle": "//h2"
    }
    class MyHandler(parslepy.base.SelectorHandler):
        _dummy = True
    mh = MyHandler()
    parselet = parslepy.Parselet(parselet_script, selector_handler=mh)

@raises(ValueError)
def test_parslepy_init_wrong_selector_handler():
    parselet_script = {
        "title": "h1",
        "subtitle": "//h2"
    }
    parselet = parslepy.Parselet(parselet_script, selector_handler=lambda s: s)

def test_parslepy_init_selector_handler_error():
    parselet_script = {
        "title": "h1",
        "subtitle": "//h2"
    }
    class MyHandler(parslepy.base.SelectorHandler):
        def make(self, selection):
            return parslepy.base.Selector(lxml.etree.XPath("body"))
        def select(self, document, selector):
            return None
        def extract(self, document, selector):
            return None

    mh = MyHandler()

    parselet = parslepy.Parselet(parselet_script, selector_handler=mh)
    assert_is_instance(parselet.selector_handler, MyHandler)



