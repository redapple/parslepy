import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
import cStringIO as StringIO
import pprint
import os
from .tools import *

def test_w3c_validator_extraction():
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


def test_creativecommon_extraction():
    debug=False
    parselets = (
        (
            {"languages": "div#languages"},
            {'languages': u'This page is available in the following languages: Castellano Castellano (Espa\xf1a) Catal\xe0 Deutsch English Esperanto fran\xe7ais hrvatski Indonesia Italiano Magyar Nederlands Norsk polski Portugu\xeas Portugu\xeas (BR) Suomeksi svenska \xedslenska \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac \u0440\u0443\u0441\u0441\u043a\u0438\u0439 \u0443\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430 \u4e2d\u6587 \u83ef\u8a9e (\u53f0\u7063) \ud55c\uad6d\uc5b4'}
        ),
        # subtle difference but there's an extra BR that is translated to "\n"
        (
            {"languages(div#languages)": "parsley:strnl(.)"},
            {'languages': u'This page is available in the following languages:\n\n\nCastellano\n\nCastellano (Espa\xf1a)\n\nCatal\xe0\n\nDeutsch\n\nEnglish\n\nEsperanto\n\nfran\xe7ais\n\nhrvatski\n\nIndonesia\n\nItaliano\n\nMagyar\n\nNederlands\n\nNorsk\n\npolski\n\nPortugu\xeas\n\nPortugu\xeas (BR)\n\nSuomeksi\n\nsvenska\n\n\xedslenska\n\n\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac\n\n\u0440\u0443\u0441\u0441\u043a\u0438\u0439\n\n\u0443\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430\n\n\u4e2d\u6587\n\n\u83ef\u8a9e (\u53f0\u7063)\n\n\ud55c\uad6d\uc5b4'}
        ),
        # all images in the page
        (
            {"images(img)": [{
                "url": "@src",
                "alt": "@alt",
                "title?": "@title",
                "style?": "@style",
                }]
            },
            {'images': [{'alt': 'cc logo', 'url': '/images/deed/cc-logo.jpg'},
                        {'alt': 'This license is acceptable for Free Cultural Works.',
                         'style': 'border: 0',
                         'url': '/images/deed/seal.png'},
                        {'alt': 'Information', 'url': '/images/information.png'}]}


        ),
    )
    hp = lxml.etree.HTMLParser()
    dirname = os.path.dirname(os.path.abspath(__file__))
    root = lxml.etree.parse(
        open(os.path.join(
                dirname,
                'data/creativecommons.org__licenses__by__3.0.html')),
        parser=hp).getroot()

    for input_parselet, expected_output in parselets:
        parselet = parslepy.Parselet(input_parselet, debug=debug)
        extracted = parselet.extract(root)
        if debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)


class test_optionality_operator():
    debug=False

    @classmethod
    def setup_class(cls):
        hp = lxml.etree.HTMLParser()
        dirname = os.path.dirname(os.path.abspath(__file__))
        cls.fp = open(
                os.path.join(dirname,
                    'data/creativecommons.org__licenses__by__3.0.html'))
        cls.root = lxml.etree.parse(cls.fp, parser=hp).getroot()

    @classmethod
    def teardown_class(cls):
        cls.fp.close()
        del cls.fp
        del cls.root

    def test_all_optional(self):
        """
        When no selector matches anything for optional keys,
        we should end up with an empty dict,
        even if the parent key is required
        """

        input_parselet, expected_output = (
            {"stuff": {
                "nothing1?": "h24",
                "nothing2?": "spanner",
                "nothing3?": "bodyboard",
            }},
            {'stuff': {}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

    def test_one_required_exists(self):
        """
        Only required keys, no optional keys

        When optional keys selectors do not match anything,
        we should only have non-empty key/values
        """

        input_parselet, expected_output = (
            {"stuff": {
                "nothing": "h1",
                "nothing2?": "spanner",
                "nothing3?": "bodyboard",
            }},
            {'stuff': {'nothing': u'Creative Commons License Deed'}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

    def test_broken_but_optional(self):
        """
        Empty dict if optional keys have broken inner-content

        An inner object might be broken (no selector match),
        but if it's for an optional key, the result is simply an empty dict
        """

        input_parselet, expected_output = (
            {"stuff?": {"perhaps": "spanner"}},
            {'stuff': {}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

    @raises(parslepy.base.NonMatchingNonOptionalKey)
    def test_broken(self):
        """
        A broken snippet must raise an Exception
        """

        input_parselet, expected_output = (
            {"stuff": {"broken": "spanner"}},
            {}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)

    @raises(parslepy.base.NonMatchingNonOptionalKey)
    def test_one_required_broken(self):
        """
        Broken content mixing required and optional keys
        """

        input_parselet, expected_output = (
            {"stuff": {
                "nothing": "paragraph",
                "nothing2?": "spanner",
                "nothing3?": "bodyboard",
            }},
            {'stuff': {}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

    @raises(parslepy.base.NonMatchingNonOptionalKey)
    def test_one_required_broken_one_matching(self):
        """
        Broken content with 1 non-matching selector
        """

        input_parselet, expected_output = (
            {"stuff": {
                "nothing": "paragraph",
                "title": "h1",
            }},
            {'stuff': {}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)

    def test_complicated(self):
        input_parselet, expected_output = (
            {"stuff": {
                "nothing?": "paragraph",
                "title": {
                    "value": "h1",
                    "novalue?": {
                        "maybe": "h47",
                    }
                }
            }},
            {'stuff': {'title': {'novalue': {},
                       'value': u'Creative Commons License Deed'}}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)
