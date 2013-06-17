import cStringIO as StringIO
from scrapy.contrib.loader import ItemLoader

class ParsleyItemLoaderConfig(object):

    def __init__(self, item_class, item_loader_class, iter_item_key=None):
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
