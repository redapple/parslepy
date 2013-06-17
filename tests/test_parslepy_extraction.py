import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
import cStringIO as StringIO
import pprint
import os


def test_extraction():
    debug = False
    parselets = (
        (
            {"title": "h1"},
            {'title': u'Markup Validation Service'}
        ),
        (
            {"httpequiv": "head meta[http-equiv] @content"},
            {'httpequiv': 'text/html;charset=utf-8'}
        ),
        (
            {"meta": ["meta @content"]},
            {'meta': [
                'text/html;charset=utf-8',
                'HTML, HyperText Markup Language, Validation,\n      W3C Markup Validation Service',
                "W3C's easy-to-use\n      markup validation service, based on SGML and XML parsers."]},
        ),
        (
            {"meta(meta)": [{"content": "@content", "name": "./@name|./@http-equiv"}],
            },
            {'meta': [
                {'content': 'text/html;charset=utf-8',
                    'name': 'Content-Type'},
                {'content': 'HTML, HyperText Markup Language, Validation,\n      W3C Markup Validation Service',
                    'name': 'keywords'},
                {'content': "W3C's easy-to-use\n      markup validation service, based on SGML and XML parsers.",
                    'name': 'description'}]}
        ),
        # 3 equivalent expressions
        (
            {"title": "#banner #title a span"},
            {'title': u'Markup Validation Service'}
        ),
        (
            {"title": "div#banner h1#title a span"},
            {'title': u'Markup Validation Service'}
        ),
        (
            {"title": "//div[@id='banner']/h1[@id='title']/a/span"},
            {'title': u'Markup Validation Service'}
        ),
        # example of nested/merge syntax
        (
            {
                "--": {
                    "--(#banner)": {
                        "--(#title)": {
                            # we need to include "span"
                            # since it's the 2nd A we're interested in
                            "--(a span)": {
                                "title": "."
                            }
                        }
                    }
                }
            },
            {'title': u'Markup Validation Service'}
        ),
        (
            {
                "title1": "#banner #title a span",
                "title2": "div#banner h1#title a span",
                "title3": "//div[@id='banner']/h1[@id='title']/a/span",
            },
            {
                'title1': u'Markup Validation Service',
                'title2': u'Markup Validation Service',
                'title3': u'Markup Validation Service',
            }
        ),
        (
            {"intro": ".intro p"},
            {'intro': u'This validator checks the markup validity of Web documents in HTML, XHTML, SMIL, MathML, etc. If you wish to validate specific content such as RSS/Atom feeds or CSS stylesheets, MobileOK content, or to find broken links, there are other validators and tools available. As an alternative you can also try our non-DTD-based validator.'}
        ),
        # first value or all or selected
        (
            {"options(select#uri-charset)": "option"},
            {'options': u'(detect automatically)'}
        ),
        (
            {"options(select#uri-charset)": ["option"]},
            {'options': [u'(detect automatically)',
                         u'utf-8 (Unicode, worldwide)',
                         u'utf-16 (Unicode, worldwide)',
                         u'iso-8859-1 (Western Europe)',
                         u'iso-8859-2 (Central Europe)',
                         u'iso-8859-3 (Southern Europe)',
                         u'iso-8859-4 (North European)',
                         u'iso-8859-5 (Cyrillic)',
                         u'iso-8859-6-i (Arabic)',
                         u'iso-8859-7 (Greek)',
                         u'iso-8859-8 (Hebrew, visual)',
                         u'iso-8859-8-i (Hebrew, logical)',
                         u'iso-8859-9 (Turkish)',
                         u'iso-8859-10 (Latin 6)',
                         u'iso-8859-11 (Latin/Thai)',
                         u'iso-8859-13 (Latin 7, Baltic Rim)',
                         u'iso-8859-14 (Latin 8, Celtic)',
                         u'iso-8859-15 (Latin 9)',
                         u'iso-8859-16 (Latin 10)',
                         u'us-ascii (basic English)',
                         u'euc-jp (Japanese, Unix)',
                         u'shift_jis (Japanese, Win/Mac)',
                         u'iso-2022-jp (Japanese, email)',
                         u'euc-kr (Korean)',
                         u'ksc_5601 (Korean)',
                         u'gb2312 (Chinese, simplified)',
                         u'gb18030 (Chinese, simplified)',
                         u'big5 (Chinese, traditional)',
                         u'Big5-HKSCS (Chinese, Hong Kong)',
                         u'tis-620 (Thai)',
                         u'koi8-r (Russian)',
                         u'koi8-u (Ukrainian)',
                         u'iso-ir-111 (Cyrillic KOI-8)',
                         u'macintosh (MacRoman)',
                         u'windows-1250 (Central Europe)',
                         u'windows-1251 (Cyrillic)',
                         u'windows-1252 (Western Europe)',
                         u'windows-1253 (Greek)',
                         u'windows-1254 (Turkish)',
                         u'windows-1255 (Hebrew)',
                         u'windows-1256 (Arabic)',
                         u'windows-1257 (Baltic Rim)']}
        ),
        (
            {"options(select#uri-charset)": "option[selected]"},
            {'options': u'(detect automatically)'}
        ),
    )
    hp = lxml.etree.HTMLParser()
    dirname = os.path.dirname(os.path.abspath(__file__))
    root = lxml.etree.parse(
        open(os.path.join(
                dirname,
                'data/validator.w3.org.html')),
        parser=hp).getroot()

    for input_parselet, expected_output in parselets:
        parselet = parslepy.Parselet(input_parselet, debug=debug)
        extracted = parselet.extract(root)
        #pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

