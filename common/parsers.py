
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser, JSONParser
from rest_framework.renderers import BaseRenderer
from rest_framework.compat import six
from django.conf import settings
from xmltodict import parse
import json
from base64 import b64decode


class RawParser(BaseRenderer):
    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            return stream.read()
        except Exception as exc:
            raise ParseError('RawParser error - %s' % six.text_type(exc))


class PlainTextParser(BaseParser):
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):

        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return data
        except Exception as exc:
            raise ParseError('PlainText error - %s' % six.text_type(exc))


class XMLParser(BaseParser):
    """
    XML parser.
    """

    media_type = 'application/xml'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as XML and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return parse(data)
        except Exception as exc:
            raise ParseError('XML parse error - %s' % six.text_type(exc))


class EnryptedJsonParser(BaseParser):
    """
    Parses JSON-serialized data.
    """

    media_type = 'application/xjson'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON and returns the resulting data.
        """
        from .crypto import MyAESCrypt
        crypt = MyAESCrypt()
        try:
            data = stream.read()
            decrypted = crypt.decrypt(b64decode(data))
            return json.loads(decrypted.decode('utf8'))
        except ValueError as exc:
            raise ParseError('JSON parse error - %s' % six.text_type(exc))
        except TypeError:
            raise ParseError("invalid content")


class ArbitraryJSONParser(JSONParser):
    media_type = '*/*'


class ArbitraryXMLParser(XMLParser):
    media_type = '*/*'