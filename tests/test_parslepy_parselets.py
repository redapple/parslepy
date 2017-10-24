import os
from parslepy.base import Parselet
from nose.tools import assert_dict_equal

html = '<html><body><h1>hi</h1><a href="/">click</a></body></html>'
expected = {"title":"hi", "link":"/"}
dirname = os.path.dirname(os.path.abspath(__file__))


def test_parslepy_from_jsonstring():
    s = '{ "title": "h1", "link": "a @href"}'
    p = Parselet.from_jsonstring(s)
    extracted = p.parse_fromstring(html)
    assert_dict_equal(extracted, expected)


def test_parslepy_from_yamlstring():
    s = '''---
    title: h1
    link: a @href
    '''
    p = Parselet.from_yamlstring(s)
    extracted = p.parse_fromstring(html)
    assert_dict_equal(extracted, expected)


def test_parslepy_from_jsonstring():
    s = '{ "title": "h1", "link": "a @href"}'
    with open(os.path.join(dirname, 'data/parselet.json')) as fp:
        p = Parselet.from_jsonfile(fp)
    extracted = p.parse_fromstring(html)
    assert_dict_equal(extracted, expected)


def test_parslepy_from_yamlstring():
    s = '''---
    title: h1
    link: a @href
    '''
    with open(os.path.join(dirname, 'data/parselet.yml')) as fp:
        p = Parselet.from_yamlfile(fp)
    extracted = p.parse_fromstring(html)
    assert_dict_equal(extracted, expected)
