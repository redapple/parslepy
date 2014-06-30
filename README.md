parslepy
========

[![Build Status](https://travis-ci.org/redapple/parslepy.png?branch=master)](https://travis-ci.org/redapple/parslepy)

*parslepy* is a Python implementation
(built on top of [lxml](http://lxml.de) and [cssselect](https://github.com/SimonSapin/cssselect)) of the
[Parsley DSL](https://github.com/fizx/parsley)
for extracting structured data from web pages, as defined by Kyle Maxwell and Andrew Cantino
(see [Parsley's wiki](https://github.com/fizx/parsley/wiki) for more details and original C implementation).

Kudos to Kyle Maxwell (@fizx) for coming up with this smart and easy syntax to define extracting rules.

> Please note that this *Parsley DSL* is **NOT** the same as the Parsley parsing library at https://pypi.python.org/pypi/Parsley

Check out the [official docs](http://pythonhosted.org/parslepy) for more information on how to install
and use *parslepy*. There is also some useful information at the [parslepy Wiki](https://github.com/redapple/parslepy/wiki)

Here is an example of a parselet script that extracts the questions from StackOverflow first page:

    {
        "first_page_questions(//div[contains(@class,'question-summary')])": [{
            "title": ".//h3/a",
            "tags": "div.tags",
            "votes": "div.votes div.mini-counts",
            "views": "div.views div.mini-counts",
            "answers": "div.status div.mini-counts"
        }]
    }

### Install

Install via pip with:

    sudo pip install parslepy

Alternatively, you can install from the latest source code:

    git clone https://github.com/redapple/parslepy.git
    sudo python setup.py install


### Online Resources ###

* [Official Documentation](http://pythonhosted.org/parslepy)
* [Wiki with examples and tutorials](https://github.com/redapple/parslepy/wiki)
* [Parsley DSL](https://github.com/fizx/parsley)
* [JSON Structure details -- Parsley wiki](https://github.com/fizx/parsley/wiki/JSON-Structure)
* [Example Scrapy Spider using Parsley](http://snipplr.com/view/67016/parsley-spider/)
* [Parsley DSL on Hacker News](https://news.ycombinator.com/item?id=1585301)

