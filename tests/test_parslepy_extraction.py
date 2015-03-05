from __future__ import unicode_literals
import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
import io as StringIO
import pprint
import os
from .tools import *

def test_w3c_validator_extraction():
    debug = False
    parselets = [
        (
            {"title": "h1"},
            {'title': 'Markup Validation Service'}
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
            {'title': 'Markup Validation Service'}
        ),
        (
            {"title": "div#banner h1#title a span"},
            {'title': 'Markup Validation Service'}
        ),
        (
            {"title": "//div[@id='banner']/h1[@id='title']/a/span"},
            {'title': 'Markup Validation Service'}
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
            {'title': 'Markup Validation Service'}
        ),
        (
            {
                "title1": "#banner #title a span",
                "title2": "div#banner h1#title a span",
                "title3": "//div[@id='banner']/h1[@id='title']/a/span",
            },
            {
                'title1': 'Markup Validation Service',
                'title2': 'Markup Validation Service',
                'title3': 'Markup Validation Service',
            }
        ),
        (
            {"intro": ".intro p"},
            {'intro': 'This validator checks the markup validity of Web documents in HTML, XHTML, SMIL, MathML, etc. If you wish to validate specific content such as RSS/Atom feeds or CSS stylesheets, MobileOK content, or to find broken links, there are other validators and tools available. As an alternative you can also try our non-DTD-based validator.'}
        ),
        # first value or all or selected
        (
            {"options(select#uri-charset)": "option"},
            {'options': '(detect automatically)'}
        ),
        (
            {"options(select#uri-charset)": ["option"]},
            {'options': ['(detect automatically)',
                         'utf-8 (Unicode, worldwide)',
                         'utf-16 (Unicode, worldwide)',
                         'iso-8859-1 (Western Europe)',
                         'iso-8859-2 (Central Europe)',
                         'iso-8859-3 (Southern Europe)',
                         'iso-8859-4 (North European)',
                         'iso-8859-5 (Cyrillic)',
                         'iso-8859-6-i (Arabic)',
                         'iso-8859-7 (Greek)',
                         'iso-8859-8 (Hebrew, visual)',
                         'iso-8859-8-i (Hebrew, logical)',
                         'iso-8859-9 (Turkish)',
                         'iso-8859-10 (Latin 6)',
                         'iso-8859-11 (Latin/Thai)',
                         'iso-8859-13 (Latin 7, Baltic Rim)',
                         'iso-8859-14 (Latin 8, Celtic)',
                         'iso-8859-15 (Latin 9)',
                         'iso-8859-16 (Latin 10)',
                         'us-ascii (basic English)',
                         'euc-jp (Japanese, Unix)',
                         'shift_jis (Japanese, Win/Mac)',
                         'iso-2022-jp (Japanese, email)',
                         'euc-kr (Korean)',
                         'ksc_5601 (Korean)',
                         'gb2312 (Chinese, simplified)',
                         'gb18030 (Chinese, simplified)',
                         'big5 (Chinese, traditional)',
                         'Big5-HKSCS (Chinese, Hong Kong)',
                         'tis-620 (Thai)',
                         'koi8-r (Russian)',
                         'koi8-u (Ukrainian)',
                         'iso-ir-111 (Cyrillic KOI-8)',
                         'macintosh (MacRoman)',
                         'windows-1250 (Central Europe)',
                         'windows-1251 (Cyrillic)',
                         'windows-1252 (Western Europe)',
                         'windows-1253 (Greek)',
                         'windows-1254 (Turkish)',
                         'windows-1255 (Hebrew)',
                         'windows-1256 (Arabic)',
                         'windows-1257 (Baltic Rim)']}
        ),
        (
            {"options(select#uri-charset)": "option[selected]"},
            {'options': '(detect automatically)'}
        ),
        # testing numerical return values
        (
            {"nb_options(select)": ["count(option)"]},
            {"nb_options": [42.0, 27.0, 42.0, 27.0, 27.0]}
        ),
        # testing boolean return values
        (
            {"imgs(img)": ["boolean(@id)"]},
            {'imgs': [  True,
                        True,
                        False,
                        False,
                        False,
                        False,
                        False,
                        False,
                ]
            }
        ),
        (
            {"imgs(img)": [
                    {
                        "has_class": "boolean(@class)",
                        "has_id": "boolean(@id)",
                        "src": "@src"
                    }
                ]
            },
            {'imgs': [
                {'has_class': False, 'has_id': True,  'src': './images/w3c.png'},
                {'has_class': True,  'has_id': True,  'src': './images/arrow-closed.png'},
                {'has_class': True,  'has_id': False, 'src': './images/arrow-closed.png'},
                {'has_class': True,  'has_id': False, 'src': './images/arrow-closed.png'},
                {'has_class': False, 'has_id': False, 'src': 'http://www.w3.org/Icons/VSlogo'},
                {'has_class': False, 'has_id': False, 'src': 'http://www.w3.org/Icons/WWW/w3c_home_nb'},
                {'has_class': False, 'has_id': False, 'src': './images/opensource-55x48.png'},
                {'has_class': False, 'has_id': False, 'src': 'http://www.w3.org/QA/Tools/I_heart_validator'}
                ]
            }
        ),

    ]

    # CSS extensions via pseudo-elements and functional pseudo-elements
    try:
        from cssselect.parser import FunctionalPseudoElement

        parselets.extend([
        (
            {"httpequiv": "head meta[http-equiv]::attr(content)"},
            {'httpequiv': 'text/html;charset=utf-8'}
        ),
        (
            {"meta": ["meta::attr(content)"]},
            {'meta': [
                'text/html;charset=utf-8',
                'HTML, HyperText Markup Language, Validation,\n      W3C Markup Validation Service',
                "W3C's easy-to-use\n      markup validation service, based on SGML and XML parsers."]},
        ),
        (
            {"meta(meta)": [{"content": "::attr(content)",
                             "name": "::attr(name), ::attr(http-equiv)"}],
            },
            {'meta': [
                {'content': 'text/html;charset=utf-8',
                    'name': 'Content-Type'},
                {'content': 'HTML, HyperText Markup Language, Validation,\n      W3C Markup Validation Service',
                    'name': 'keywords'},
                {'content': "W3C's easy-to-use\n      markup validation service, based on SGML and XML parsers.",
                    'name': 'description'}]}
        ),
        (
            {"title": "#banner #title a span::text"},
            {'title': 'Markup Validation Service'}
        ),
        (
            {"comment": "::comment"},
            {'comment': 'invisible'}
        ),
        (
            {"comments": ["::comment"]},
            {'comments': ['invisible',
                         '<br /><label for="parsemodel">Treat as:</label> <select id="parsemodel" name="parsemodel"> <option value="sgml">HTML</option> <option value="xml">XML (and XHTML)</option> </select>',
                         'fields',
                         'frontforms']}
        ),
        ])
    except:
        pass

    hp = lxml.etree.HTMLParser()
    dirname = os.path.dirname(os.path.abspath(__file__))
    root = lxml.etree.parse(
        open(os.path.join(
                dirname,
                'data/validator.w3.org.html')),
        parser=hp).getroot()
    for input_parselet, expected_output in parselets:
        yield compare_extracted_output, root, input_parselet, expected_output

def compare_extracted_output(root, input_parselet, expected_output, debug=False):
    parselet = parslepy.Parselet(input_parselet, strict=True, debug=debug)
    extracted = parselet.extract(root)
    print("extracted:", [extracted])
    print("expected_output:", [expected_output])
    assert_dict_equal(extracted, expected_output)


def test_creativecommon_extraction():
    debug=False
    parselets = (
        (
            {"languages": "div#languages"},
            {'languages': 'This page is available in the following languages: Castellano Castellano (Espa\u00f1a) Catal\u00e0 Deutsch English Esperanto fran\u00e7ais hrvatski Indonesia Italiano Magyar Nederlands Norsk polski Portugu\u00eas Portugu\u00eas (BR) Suomeksi svenska \u00edslenska \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac \u0440\u0443\u0441\u0441\u043a\u0438\u0439 \u0443\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430 \u4e2d\u6587 \u83ef\u8a9e (\u53f0\u7063) \ud55c\uad6d\uc5b4'}
        ),
        # subtle difference but there's an extra BR that is translated to "\n"
        (
            {"languages(div#languages)": "parsley:strnl(.)"},
            {'languages': 'This page is available in the following languages:\n\n\nCastellano\n\nCastellano (Espa\u00f1a)\n\nCatal\u00e0\n\nDeutsch\n\nEnglish\n\nEsperanto\n\nfran\u00e7ais\n\nhrvatski\n\nIndonesia\n\nItaliano\n\nMagyar\n\nNederlands\n\nNorsk\n\npolski\n\nPortugu\u00eas\n\nPortugu\u00eas (BR)\n\nSuomeksi\n\nsvenska\n\n\u00edslenska\n\n\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac\n\n\u0440\u0443\u0441\u0441\u043a\u0438\u0439\n\n\u0443\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430\n\n\u4e2d\u6587\n\n\u83ef\u8a9e (\u53f0\u7063)\n\n\ud55c\uad6d\uc5b4'}
        ),
        # HTML code output
        (
            {"h1": "parsley:html(//h1)"},
            {'h1': '<h1><span>Creative Commons License Deed</span></h1>'}
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
        # strip brackets on element text content
        (
            {
                "ccby": "//div[@id='deed-license']/h2/span[2]",
                "ccby_str": "parsley:str(//div[@id='deed-license']/h2/span[2])",
                "ccby_stripped": "parsley:strip(//div[@id='deed-license']/h2/span[2], '()')",
                "ccby_str_stripped": "parsley:strip(parsley:str(//div[@id='deed-license']/h2/span[2]), '()')",
            },
            {
                "ccby": "(CC BY 3.0)",
                "ccby_str": "(CC BY 3.0)",
                "ccby_stripped": "CC BY 3.0",
                "ccby_str_stripped": "CC BY 3.0",
            }
        ),
        # strip on element attributes
        # get the last 10 links and strip "." and "/" characters
        # NOTE: this is not really a realistic use-case but it shows
        #       how powerful XPath expressions can be
        (
            {
                "links": ["(//a)[position() > (last() - 10)]/@href"],
                "links_stripped": ["parsley:strip((//a)[position() > (last() - 10)]/@href, '/.')"],
            },
            {
                'links': [
                    './deed.pt_BR',
                    './deed.fi',
                    './deed.sv',
                    './deed.is',
                    './deed.el',
                    './deed.ru',
                    './deed.uk',
                    './deed.zh',
                    './deed.zh_TW',
                    './deed.ko'
                    ],
                'links_stripped': [
                    'deed.pt_BR',
                    'deed.fi',
                    'deed.sv',
                    'deed.is',
                    'deed.el',
                    'deed.ru',
                    'deed.uk',
                    'deed.zh',
                    'deed.zh_TW',
                    'deed.ko'
                ],
            }
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
        yield compare_extracted_output, root, input_parselet, expected_output


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
            {'stuff': {'nothing': 'Creative Commons License Deed'}}
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
                       'value': 'Creative Commons License Deed'}}}
        )
        parselet = parslepy.Parselet(input_parselet, strict=True, debug=self.debug)
        extracted = parselet.extract(self.root)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)


class test_xml_extraction(object):
    debug=False

    @classmethod
    def setup_class(cls):
        hp = lxml.etree.XMLParser()
        dirname = os.path.dirname(os.path.abspath(__file__))
        cls.fp = open(
                os.path.join(dirname,
                    'data/itunes.topalbums.rss'))
        cls.docroot = lxml.etree.parse(cls.fp, parser=hp).getroot()

    @classmethod
    def teardown_class(cls):
        del cls.docroot
        cls.fp.close()
        del cls.fp


    def test_itunes_top_albums(self):
        input_parselet, expected_output = (
            {"entries(//atom:feed/atom:entry)": [{
                    "title": "atom:title",
                    "name": "im:name",
                    "id": "atom:id/@im:id",
                    "artist(im:artist)": {
                        "name": ".",
                        "href": "@href",
                    },
                    "images(im:image)": [{
                        "height": "@height",
                        "url": ".",
                    }],
                    #"content": "atom:content[@type='html']"
                    "releasedate": "im:releaseDate",
                }]
            },
            {'entries': [{'artist': {'href': 'https://itunes.apple.com/us/artist/wale/id129335935?uo=2',
                                     'name': 'Wale'},
                          'id': '647928068',
                          'images': [{'height': '55',
                                      'url': 'http://a815.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1537.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a976.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.170x170-75.jpg'}],
                          'name': 'The Gifted',
                          'releasedate': '2013-06-24T00:00:00-07:00',
                          'title': 'The Gifted - Wale'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/kanye-west/id2715720?uo=2',
                                     'name': 'Kanye West'},
                          'id': '662392801',
                          'images': [{'height': '55',
                                      'url': 'http://a697.phobos.apple.com/us/r1000/033/Music4/v4/b8/fc/be/b8fcbe49-510d-8afe-7c34-fa268da339f2/UMG_cvrart_00602537439317_01_RGB72_1500x1500_13UAAIM08444.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1419.phobos.apple.com/us/r1000/033/Music4/v4/b8/fc/be/b8fcbe49-510d-8afe-7c34-fa268da339f2/UMG_cvrart_00602537439317_01_RGB72_1500x1500_13UAAIM08444.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a1930.phobos.apple.com/us/r1000/033/Music4/v4/b8/fc/be/b8fcbe49-510d-8afe-7c34-fa268da339f2/UMG_cvrart_00602537439317_01_RGB72_1500x1500_13UAAIM08444.170x170-75.jpg'}],
                          'name': 'Yeezus',
                          'releasedate': '2013-06-18T00:00:00-07:00',
                          'title': 'Yeezus - Kanye West'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/j-cole/id73705833?uo=2',
                                     'name': 'J Cole'},
                          'id': '651105499',
                          'images': [{'height': '55',
                                      'url': 'http://a537.phobos.apple.com/us/r30/Music2/v4/c5/03/68/c5036883-38b9-702c-baf0-876db639b1f9/886444025935.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1259.phobos.apple.com/us/r30/Music2/v4/c5/03/68/c5036883-38b9-702c-baf0-876db639b1f9/886444025935.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a1354.phobos.apple.com/us/r30/Music2/v4/c5/03/68/c5036883-38b9-702c-baf0-876db639b1f9/886444025935.170x170-75.jpg'}],
                          'name': 'Born Sinner (Deluxe Version)',
                          'releasedate': '2013-06-14T00:00:00-07:00',
                          'title': 'Born Sinner (Deluxe Version) - J Cole'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/august-burns-red/id47796394?uo=2',
                                     'name': 'August Burns Red'},
                          'id': '655052532',
                          'images': [{'height': '55',
                                      'url': 'http://a854.phobos.apple.com/us/r30/Music2/v4/05/81/64/05816462-e832-80e4-9fa1-554d9bdd2542/886443989689.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1576.phobos.apple.com/us/r30/Music2/v4/05/81/64/05816462-e832-80e4-9fa1-554d9bdd2542/886443989689.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a359.phobos.apple.com/us/r30/Music2/v4/05/81/64/05816462-e832-80e4-9fa1-554d9bdd2542/886443989689.170x170-75.jpg'}],
                          'name': 'Rescue & Restore',
                          'releasedate': '2013-06-25T00:00:00-07:00',
                          'title': 'Rescue & Restore - August Burns Red'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/mac-miller/id419944559?uo=2',
                                     'name': 'Mac Miller'},
                          'id': '650864146',
                          'images': [{'height': '55',
                                      'url': 'http://a1599.phobos.apple.com/us/r30/Music/v4/7c/03/68/7c03681e-3cb6-23cb-5584-5b9dd42e54f7/040232021398_Cover.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a321.phobos.apple.com/us/r30/Music/v4/7c/03/68/7c03681e-3cb6-23cb-5584-5b9dd42e54f7/040232021398_Cover.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a1696.phobos.apple.com/us/r30/Music/v4/7c/03/68/7c03681e-3cb6-23cb-5584-5b9dd42e54f7/040232021398_Cover.170x170-75.jpg'}],
                          'name': 'Watching Movies With the Sound Off (Deluxe Edition)',
                          'releasedate': '2013-06-18T00:00:00-07:00',
                          'title': 'Watching Movies With the Sound Off (Deluxe Edition) - Mac Miller'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/daft-punk/id5468295?uo=2',
                                     'name': 'Daft Punk'},
                          'id': '617154241',
                          'images': [{'height': '55',
                                      'url': 'http://a1849.phobos.apple.com/us/r1000/096/Music2/v4/52/aa/50/52aa5008-4934-0c27-a08d-8ebd7d13c030/886443919266.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a923.phobos.apple.com/us/r1000/096/Music2/v4/52/aa/50/52aa5008-4934-0c27-a08d-8ebd7d13c030/886443919266.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a1450.phobos.apple.com/us/r1000/096/Music2/v4/52/aa/50/52aa5008-4934-0c27-a08d-8ebd7d13c030/886443919266.170x170-75.jpg'}],
                          'name': 'Random Access Memories',
                          'releasedate': '2013-05-21T00:00:00-07:00',
                          'title': 'Random Access Memories - Daft Punk'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/skillet/id1750802?uo=2',
                                     'name': 'Skillet'},
                          'id': '655774977',
                          'images': [{'height': '55',
                                      'url': 'http://a545.phobos.apple.com/us/r1000/050/Music/v4/b8/3f/7b/b83f7b74-4e7a-6b06-9385-667dc1288d7d/075679954787.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1267.phobos.apple.com/us/r1000/050/Music/v4/b8/3f/7b/b83f7b74-4e7a-6b06-9385-667dc1288d7d/075679954787.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a114.phobos.apple.com/us/r1000/050/Music/v4/b8/3f/7b/b83f7b74-4e7a-6b06-9385-667dc1288d7d/075679954787.170x170-75.jpg'}],
                          'name': 'Rise',
                          'releasedate': '2013-06-21T00:00:00-07:00',
                          'title': 'Rise - Skillet'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/skillet/id1750802?uo=2',
                                     'name': 'Skillet'},
                          'id': '662457451',
                          'images': [{'height': '55',
                                      'url': 'http://a399.phobos.apple.com/us/r1000/022/Music/v4/87/3e/eb/873eebf6-618c-d8e1-b8df-4d0b60f6729b/075679954749.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1473.phobos.apple.com/us/r1000/022/Music/v4/87/3e/eb/873eebf6-618c-d8e1-b8df-4d0b60f6729b/075679954749.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a880.phobos.apple.com/us/r1000/022/Music/v4/87/3e/eb/873eebf6-618c-d8e1-b8df-4d0b60f6729b/075679954749.170x170-75.jpg'}],
                          'name': 'Rise (Deluxe Version)',
                          'releasedate': '2013-06-21T00:00:00-07:00',
                          'title': 'Rise (Deluxe Version) - Skillet'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/attila/id46893195?uo=2',
                                     'name': 'Attila'},
                          'id': '649587514',
                          'images': [{'height': '55',
                                      'url': 'http://a608.phobos.apple.com/us/r30/Music/v4/ee/7d/b2/ee7db2ad-e783-2c3a-2ad3-6549868315e7/793018342834.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a1682.phobos.apple.com/us/r30/Music/v4/ee/7d/b2/ee7db2ad-e783-2c3a-2ad3-6549868315e7/793018342834.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a1297.phobos.apple.com/us/r30/Music/v4/ee/7d/b2/ee7db2ad-e783-2c3a-2ad3-6549868315e7/793018342834.170x170-75.jpg'}],
                          'name': 'About That Life',
                          'releasedate': '2013-06-25T00:00:00-07:00',
                          'title': 'About That Life - Attila'},
                         {'artist': {'href': 'https://itunes.apple.com/us/artist/india.arie/id92325?uo=2',
                                     'name': 'India.Arie'},
                          'id': '659585460',
                          'images': [{'height': '55',
                                      'url': 'http://a1694.phobos.apple.com/us/r30/Music/v4/d5/65/b2/d565b212-4463-6486-7ee2-eeab22ff3d87/UMG_cvrart_00602537429486_01_RGB72_1500x1500_13UAAIM06584.55x55-70.jpg'},
                                     {'height': '60',
                                      'url': 'http://a768.phobos.apple.com/us/r30/Music/v4/d5/65/b2/d565b212-4463-6486-7ee2-eeab22ff3d87/UMG_cvrart_00602537429486_01_RGB72_1500x1500_13UAAIM06584.60x60-50.jpg'},
                                     {'height': '170',
                                      'url': 'http://a63.phobos.apple.com/us/r30/Music/v4/d5/65/b2/d565b212-4463-6486-7ee2-eeab22ff3d87/UMG_cvrart_00602537429486_01_RGB72_1500x1500_13UAAIM06584.170x170-75.jpg'}],
                          'name': 'SongVersation (Deluxe Edition)',
                          'releasedate': '2013-06-25T00:00:00-07:00',
                          'title': 'SongVersation (Deluxe Edition) - India.Arie'}]}
        )
        xsh = parslepy.selectors.XPathSelectorHandler(
            namespaces={
                'atom': 'http://www.w3.org/2005/Atom',
                'im': 'http://itunes.apple.com/rss'
            })
        parselet = parslepy.Parselet(
            input_parselet, selector_handler=xsh, strict=True,
            debug=self.debug)
        extracted = parselet.extract(self.docroot)
        if self.debug:
            pprint.pprint(extracted)
        assert_dict_equal(extracted, expected_output)
