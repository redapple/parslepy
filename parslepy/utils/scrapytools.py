import cStringIO as StringIO
from scrapy.contrib.loader import ItemLoader
from scrapy.item import Item, Field
from scrapy.http import Request
import urlparse
import pprint

class ParsleyItemLoaderConfig(object):

    def __init__(self, item_class=None, item_loader_class=None, iter_item_key=None):
        self.item_class = item_class
        self.item_loader_class = item_loader_class
        self.iter_item_key = iter_item_key

    def __repr__(self):
        return u"<ParsleyItemLoaderConfig: item=%s, loader=%s, key=%s>" % (
                self.item_class, self.item_loader_class, self.iter_item_key)

class ParsleyItemClassLoader(object):
    def __init__(self, parselet, configs, response=None, **context):

        self.configs = configs
        self.parselet = parselet
        self.response = response
        self.extracted = None
        self.context = context

    def _extract(self, response=None):
        self.extracted = self.parselet.parse(
            StringIO.StringIO(response.body))


    def iter_items(self, response=None):
        if self.extracted is None:
            self._extract(response or self.response)

        for config in self.configs:
            if config.iter_item_key is None:
                loader = config.item_loader_class(config.item_class(),
                    **self.context)
                loader.add_value(None, self.extracted)
                yield loader.load_item()
            else:
                for item_value in self.extracted.get(config.iter_item_key) or self.extracted:
                    loader = config.item_loader_class(config.item_class(),
                        **self.context)
                    loader.add_value(None, item_value)
                    yield loader.load_item()


class ParsleyImplicitItemClassLoader(object):
    def __init__(self, parselet, configs=None, response=None, **context):

        self.configs = configs
        self.parselet = parselet
        self.response = response
        self.extracted = None
        self.context = context

    def _generate_item_classes(self, extracted):
        for config in self.configs:
            if config.iter_item_key:
                keys = [
                    k
                    for e in extracted.get(config.iter_item_key)
                    for k in e.iterkeys()
                ]
                class_name = "%sClass" % config.iter_item_key.capitalize()
            else:
                keys = extracted.keys()
                class_name = "CustomClass"

            if keys:
                print "keys:", set(keys)
                config.item_class = type(
                    class_name,
                    (Item,),
                    dict([(k, Field()) for k in set(keys)]))
                #print config.item_class

    def _parse(self, response=None):
        return self.parselet.parse(
            StringIO.StringIO(response.body))

    def iter_items(self, response=None):
        extracted = self._parse(response or self.response)

        # generate Item classes based on Parsley structure
        self._generate_item_classes(extracted)

        for config in self.configs:
            if not config.item_class:
                continue
            if config.iter_item_key is None:
                yield config.item_class(**extracted)
            else:
                #print extracted
                for item_value in extracted.get(config.iter_item_key):
                    yield config.item_class(**item_value)
        del extracted

    def iter_requests(self, response=None, iter_request_key=None, get_url_function=None, request_callback=None):

        extracted = self._parse(response or self.response)

        if get_url_function is None:
            get_url_function = lambda x: x

        #pprint.pprint(self.extracted)
        for request_info in extracted.get(iter_request_key):
            yield Request(
                url=urlparse.urljoin(
                            response.url,
                            get_url_function(request_info)),
                callback=request_callback)
        del extracted
