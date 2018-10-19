from rest_framework.renderers import BaseRenderer, JSONRenderer
from xmltodict import unparse
from .encoders import MongoJsonEncoder


class PlainTextRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return str(data).encode(self.charset)


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """
    media_type = 'application/xml'
    format = 'xml'
    root = 'xml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders *obj* into serialized XML.
        """
        if self.root:
            data = {self.root: data}
        return unparse(data).encode(self.charset)


class BareXMLRenderer(XMLRenderer):
    root = None


class MongoJsonRenderer(JSONRenderer):
    encoder_class = MongoJsonEncoder
