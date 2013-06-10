#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import pprint
import parslepy
import lxml.html

def main():

    parser = optparse.OptionParser()
    parser.add_option("--debug", dest="debug", action="store_true", help="debug mode", default=False)
    parser.add_option("--url", dest="url", help="fetch this URL", default=None)
    parser.add_option("--script", dest="parselet", help="Parsley script filename", default=None)

    (options, args) = parser.parse_args()

    if not options.parselet:
        print "You must provide a Parsley script"
        return
    if not options.url:
        print "You must provide an URL"
        return

    root = lxml.html.parse(options.url).getroot()

    with open(options.parselet) as fp:
        extractor = parslepy.ParsleyExtractor.from_jsonfile(fp, options.debug)
        output = extractor.extract(root)
        pprint.pprint(output)

if __name__ == '__main__':
	main()

