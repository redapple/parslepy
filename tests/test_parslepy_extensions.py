from __future__ import unicode_literals
import parslepy
import parslepy.base
import lxml.cssselect
from nose.tools import *
import io as StringIO
import pprint
import os
from .tools import *

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

def compare_extracted_output(root, input_parselet, expected_output, debug=False):
    parselet = parslepy.Parselet(input_parselet, strict=True, debug=debug)
    extracted = parselet.extract(root)
    assert_dict_equal(extracted, expected_output)
