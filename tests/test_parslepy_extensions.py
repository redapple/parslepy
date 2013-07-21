from __future__ import unicode_literals
import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
import io as StringIO
import pprint
import os
from .tools import *

def compare_extracted_output(root, input_parselet, expected_output, debug=False):
    parselet = parslepy.Parselet(input_parselet, strict=True, debug=debug)
    extracted = parselet.extract(root)
    #pprint.pprint(extracted)
    #pprint.pprint(expected_output)
    assert_dict_equal(extracted, expected_output)

def test_attrnames():
    parselets = (
        (
            {"images(img)": [{
                    "attrnames": ["parslepy:attrname(@*)"],
                    "attrvals": ["@*"],
                }]},
            {
                'images': [
                    {
                        'attrvals': ['W3C', '110', '61', 'logo', './images/w3c.png'],
                        'attrnames': ['alt', 'width', 'height', 'id', 'src']
                    },
                    {
                        'attrvals': ['toggleiconURI', 'toggleicon', './images/arrow-closed.png', 'Show'],
                        'attrnames': ['id', 'class', 'src', 'alt']
                    },
                    {
                        'attrvals': ['toggleicon', './images/arrow-closed.png', 'Show'],
                        'attrnames': ['class', 'src', 'alt']
                    },
                    {
                        'attrvals': ['toggleicon', './images/arrow-closed.png', 'Show'],
                        'attrnames': ['class', 'src', 'alt']
                    },
                    {
                        'attrvals': ['http://www.w3.org/Icons/VSlogo', 'W3C Validator\nSuite Logo'],
                        'attrnames': ['src', 'alt']
                    },
                    {
                        'attrvals': ['http://www.w3.org/Icons/WWW/w3c_home_nb', 'W3C', '72', '47'],
                        'attrnames': ['src', 'alt', 'width', 'height']
                    },
                    {
                        'attrvals': ['./images/opensource-55x48.png', 'Open-Source', 'We are building certified Open Source/Free Software. - see www.opensource.org', '55', '48'],
                        'attrnames': ['src', 'alt', 'title', 'width', 'height']
                    },
                    {
                        'attrvals': ['http://www.w3.org/QA/Tools/I_heart_validator', 'I heart Validator logo', ' Validators Donation Program', '80', '15'],
                        'attrnames': ['src', 'alt', 'title', 'width', 'height']
                    }
                ]
            }
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
        yield compare_extracted_output, root, input_parselet, expected_output


def test_to_content():
    parselets = (
        (
            {"intro": 'parslepy:html(//div[@class="intro"])'},
            {'intro': """<div class="intro">
    <p>
        This validator checks the
        <a href="docs/help.html#validation_basics" title="What is markup validation?">markup validity</a>
        of Web documents in HTML, XHTML, SMIL, MathML, etc.
        If you wish to validate specific content such as
        <a href="http://validator.w3.org/feed/" title="Feed validator, hosted at W3C">RSS/Atom feeds</a> or
    <a href="http://jigsaw.w3.org/css-validator/" title="W3C CSS Validation Service">CSS stylesheets</a>,
    <a href="http://validator.w3.org/mobile/" title="MobileOK Checker">MobileOK content</a>,
        or to <a href="http://validator.w3.org/checklink" title="W3C Link Checker">find broken links</a>,
 there are <a href="http://www.w3.org/QA/Tools/">other validators and tools</a> available.
    As an alternative you can also try our <a href="http://validator.w3.org/nu">non-DTD-based validator</a>.
    </p>
</div>"""},
        ),
        (
            {"intro": 'parslepy:text(//div[@class="intro"])'},
            {'intro': 'This validator checks the markup validity of Web documents in HTML, XHTML, SMIL, MathML, etc. If you wish to validate specific content such as RSS/Atom feeds or CSS stylesheets, MobileOK content, or to find broken links, there are other validators and tools available. As an alternative you can also try our non-DTD-based validator.'}
        ),
        (
            {"intro": 'parslepy:textnl(//div[@class="intro"])'},
            {'intro': """This validator checks the
markup validity
of Web documents in HTML, XHTML, SMIL, MathML, etc.
If you wish to validate specific content such as
RSS/Atom feeds or
CSS stylesheets,
MobileOK content,
or to find broken links,
there are other validators and tools available.
As an alternative you can also try our non-DTD-based validator."""
            }
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
        yield compare_extracted_output, root, input_parselet, expected_output

def test_to_xml():
    parselets = (
        (
            {"first": "parslepy:xml(//atom:feed/atom:entry[1]/im:contentType)"},
            {'first': '<im:contentType xmlns:im="http://itunes.apple.com/rss" xmlns="http://www.w3.org/2005/Atom" term="Music" label="Music"><im:contentType term="Album" label="Album"/></im:contentType>'}
        ),
    )
    dirname = os.path.dirname(os.path.abspath(__file__))
    root = lxml.etree.parse(
        open(os.path.join(
                dirname,
                'data/itunes.topalbums.rss')),
        parser=lxml.etree.XMLParser()).getroot()
    xsh = parslepy.selectors.XPathSelectorHandler(
        namespaces={
            'atom': 'http://www.w3.org/2005/Atom',
            'im': 'http://itunes.apple.com/rss'
        })
    for input_parselet, expected_output in parselets:
        parselet = parslepy.Parselet(
            input_parselet, selector_handler=xsh, strict=True)
        extracted = parselet.extract(root)
        assert_dict_equal(extracted, expected_output)


def test_userdefined_extensions():

    def myattrnames(ctx, xpctx, attributes, *args):
        #print "myattrnames:", ctx, xpctx, attributes, args
        return [a.attrname for a in attributes]

    # extension to built full URLs from @href or @src attributes
    try:
        import urlparse     # Python 2.x
    except ImportError:
        import urllib.parse as urlparse

    def absurl(ctx, xpctx, attributes, *args):
        #print "absurl:", ctx, xpctx, attributes, args
        return [urlparse.urljoin(ctx, u) for u in attributes]

    parselets = (
        (
            {
                "head_meta(head/meta)": [{
                    "attrnames": ["myext:attrnames(@*)"],
                    "attrvals": ["@*"],
                }],
                "img_links": ["//img/@src"],
                "img_abslinks": ["myext:absurl(//img/@src)"],
            },
            {
                'head_meta': [
                    {'attrnames': ['http-equiv', 'content'],
                     'attrvals': ['Content-Type', 'text/html;charset=utf-8']
                    },
                    {'attrnames': ['name', 'content'],
                     'attrvals': ['keywords',
                                  'HTML, HyperText Markup Language, Validation,\n      W3C Markup Validation Service']},
                    {'attrnames': ['name', 'content'],
                     'attrvals': ['description',
                                   "W3C's easy-to-use\n      markup validation service, based on SGML and XML parsers."]}],
                'img_abslinks': ['http://validator.w3.org/images/w3c.png',
                               'http://validator.w3.org/images/arrow-closed.png',
                               'http://validator.w3.org/images/arrow-closed.png',
                               'http://validator.w3.org/images/arrow-closed.png',
                               'http://www.w3.org/Icons/VSlogo',
                               'http://www.w3.org/Icons/WWW/w3c_home_nb',
                               'http://validator.w3.org/images/opensource-55x48.png',
                               'http://www.w3.org/QA/Tools/I_heart_validator'],
                'img_links': ['./images/w3c.png',
                            './images/arrow-closed.png',
                            './images/arrow-closed.png',
                            './images/arrow-closed.png',
                            'http://www.w3.org/Icons/VSlogo',
                            'http://www.w3.org/Icons/WWW/w3c_home_nb',
                            './images/opensource-55x48.png',
                            'http://www.w3.org/QA/Tools/I_heart_validator']
            }
        ),
    )
    mynamespaces = {
        "myext": "myextension"
    }
    myextensions = {
        ("myextension", "absurl"): absurl,
        ("myextension", "attrnames"): myattrnames,
    }

    sh = parslepy.DefaultSelectorHandler(
        namespaces=mynamespaces,
        extensions=myextensions)

    dirname = os.path.dirname(os.path.abspath(__file__))
    for input_parselet, expected_output in parselets:
        parselet = parslepy.Parselet(
            input_parselet,
            selector_handler=sh, strict=True)
        extracted = parselet.parse(
            os.path.join(dirname, 'data/validator.w3.org.html'),
            context='http://validator.w3.org/')

        #pprint.pprint(extracted)
        #pprint.pprint(expected_output)
        assert_dict_equal(extracted, expected_output)
