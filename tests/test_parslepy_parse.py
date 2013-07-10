from __future__ import unicode_literals
import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
from .tools import *
import pprint
import os


def test_parslepy_xpathparse_xml_file():
    parselet_script = {"id": "//atom:id"}
    xsh = parslepy.selectors.XPathSelectorHandler(
                namespaces={'atom': 'http://www.w3.org/2005/Atom'}
            )
    dirname = os.path.dirname(os.path.abspath(__file__))
    fp = open(os.path.join(dirname, 'data/itunes.topalbums.rss'))

    expected = {
        'id': 'https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml'
    }

    parselet = parslepy.Parselet(parselet_script, selector_handler=xsh)
    extracted = parselet.parse(fp, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)


def test_parslepy_defaultparse_xml_file():
    parselet_script = {"id": "//atom:id"}
    dsh = parslepy.selectors.DefaultSelectorHandler(
                namespaces={'atom': 'http://www.w3.org/2005/Atom'}
            )
    dirname = os.path.dirname(os.path.abspath(__file__))
    fp = open(os.path.join(dirname, 'data/itunes.topalbums.rss'))

    expected = {
        'id': 'https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml'
    }

    parselet = parslepy.Parselet(parselet_script, selector_handler=dsh)
    extracted = parselet.parse(fp, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)


def test_parslepy_defaultparse_xml_file_cssselectors():
    parselet_script = {"id": "atom|id", "imid": "atom|id @im|id"}
    dsh = parslepy.selectors.DefaultSelectorHandler(
                namespaces={
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
                }
            )
    dirname = os.path.dirname(os.path.abspath(__file__))
    fp = open(os.path.join(dirname, 'data/itunes.topalbums.rss'))

    expected = {
        'id': 'https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml',
        'imid': '647928068',
    }

    parselet = parslepy.Parselet(parselet_script, selector_handler=dsh)
    extracted = parselet.parse(fp, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)


xmldoc = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns:im="http://itunes.apple.com/rss" xmlns="http://www.w3.org/2005/Atom" xml:lang="en">
<id>https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml</id><title>iTunes Store: Top Albums</title><updated>2013-06-25T06:27:25-07:00</updated><link rel="alternate" type="text/html" href="https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?cc=us&amp;id=38&amp;popId=11"/><link rel="self" href="https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml"/><icon>http://itunes.apple.com/favicon.ico</icon><author><name>iTunes Store</name><uri>http://www.apple.com/itunes/</uri></author><rights>Copyright 2008 Apple Inc.</rights>
<entry>
    <updated>2013-06-25T06:27:25-07:00</updated>
    <id im:id="647928068">https://itunes.apple.com/us/album/the-gifted/id647928068?uo=2</id>
    <title>The Gifted - Wale</title>
    <im:name>The Gifted</im:name>
    <im:image height="55">http://a815.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.55x55-70.jpg</im:image>
    <im:image height="60">http://a1537.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.60x60-50.jpg</im:image>
    <im:image height="170">http://a976.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.170x170-75.jpg</im:image>
</entry>
</feed>
"""

def test_parslepy_xpathparse_xml_fromstring():

    parselet_script = {
        "--(//atom:feed/atom:entry)": {
            "title": "atom:title",
            "name": "im:name",
            "id": "atom:id/@im:id",
            "images(im:image)": [{
                "height": "@height",
                "url": ".",
            }],
            "releasedate": "im:releaseDate",
        }
    }
    xsh = parslepy.selectors.XPathSelectorHandler(
                namespaces={
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
                }
            )

    expected = {
        'id': '647928068',
        'images': [
            {   'height': '55',
                'url': 'http://a815.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.55x55-70.jpg'
            },
            {   'height': '60',
                'url': 'http://a1537.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.60x60-50.jpg'
            },
            {   'height': '170',
                'url': 'http://a976.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.170x170-75.jpg'
            }
        ],
        'name': 'The Gifted',
        'title': 'The Gifted - Wale',
    }
    parselet = parslepy.Parselet(parselet_script, selector_handler=xsh)
    extracted = parselet.parse_fromstring(xmldoc, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)


def test_parslepy_defaultparse_xml_fromstring():

    parselet_script = {
        "--(//atom:feed/atom:entry)": {
            "title": "atom:title",
            "name": "im:name",
            "id": "atom:id/@im:id",
            "images(im:image)": [{
                "height": "@height",
                "url": ".",
            }],
            "releasedate": "im:releaseDate",
        }
    }
    dsh = parslepy.selectors.DefaultSelectorHandler(
                namespaces={
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
                }
            )

    expected = {
        'id': '647928068',
        'images': [
            {   'height': '55',
                'url': 'http://a815.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.55x55-70.jpg'
            },
            {   'height': '60',
                'url': 'http://a1537.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.60x60-50.jpg'
            },
            {   'height': '170',
                'url': 'http://a976.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.170x170-75.jpg'
            }
        ],
        'name': 'The Gifted',
        'title': 'The Gifted - Wale',
    }
    parselet = parslepy.Parselet(parselet_script, selector_handler=dsh)
    extracted = parselet.parse_fromstring(xmldoc, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)


def test_parslepy_defaultparse_xml_fromstring_cssselectors():

    parselet_script = {
        "--(atom|feed atom|entry)": {
            "title": "atom|title",
            "name": "im|name",
            "id": "atom|id @im|id",
            "images(im|image)": [{
                "height": "@height",
                "url": ".",
            }],
            "releasedate": "im|releaseDate",
        }
    }
    dsh = parslepy.selectors.DefaultSelectorHandler(
                namespaces={
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss',
                }
            )

    expected = {
        'id': '647928068',
        'images': [
            {   'height': '55',
                'url': 'http://a815.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.55x55-70.jpg'
            },
            {   'height': '60',
                'url': 'http://a1537.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.60x60-50.jpg'
            },
            {   'height': '170',
                'url': 'http://a976.phobos.apple.com/us/r30/Features/v4/02/cc/73/02cc7370-693c-f0fe-505b-bb84043ce186/dj.pehmruyt.170x170-75.jpg'
            }
        ],
        'name': 'The Gifted',
        'title': 'The Gifted - Wale',
    }
    parselet = parslepy.Parselet(parselet_script, selector_handler=dsh)
    extracted = parselet.parse_fromstring(xmldoc, parser=lxml.etree.XMLParser())
    assert_dict_equal(extracted, expected)




def test_parslepy_parse_html_file():

    parselet = parslepy.Parselet({"title": "h1"})
    expected = {'title': 'Markup Validation Service'}

    dirname = os.path.dirname(os.path.abspath(__file__))
    extracted = parselet.parse(
                    open(os.path.join(dirname, 'data/validator.w3.org.html'))
                )
    assert_dict_equal(extracted, expected)


def test_parslepy_parse_html_fromstring():

    htmldoc = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <title>The W3C Markup Validation Service</title>
    <link rev="made" href="mailto:www-validator@w3.org" />
    <link rel="shortcut icon" href="http://www.w3.org/2008/site/images/favicon.ico" type="image/x-icon" />
    <link rev="start" href="./" title="Home Page" />
    <style type="text/css" media="all">
      @import "./style/base";
    </style>
    <script type="text/javascript" src="scripts/combined"></script>
    <meta name="keywords" content="HTML, HyperText Markup Language, Validation,
      W3C Markup Validation Service" />
    <meta name="description" content="W3C's easy-to-use
      markup validation service, based on SGML and XML parsers." />

    <link rel="alternate" type="application/atom+xml" href="http://www.w3.org/QA/Tools/validator-whatsnew.atom" />
  </head>
  <body>
   <div id="banner">
    <h1 id="title">
      <a href="http://www.w3.org/"><img alt="W3C" width="110" height="61" id="logo" src="./images/w3c.png" /></a>
			<a href="./"><span>Markup Validation Service</span></a>
      </h1>
      <p id="tagline">Check the markup (HTML, XHTML, ...) of Web documents</p>
   </div>
  </body>
</html>
    """

    parselet = parslepy.Parselet(
        {
            "title": "h1",
            "pid": "p[id] @id"
        })
    expected = {
        'title': 'Markup Validation Service',
        'pid': 'tagline'
    }

    extracted = parselet.parse_fromstring(htmldoc)
    assert_dict_equal(extracted, expected)
