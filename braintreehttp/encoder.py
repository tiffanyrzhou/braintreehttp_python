import re
import os


class Encoder(object):

    def __init__(self, encoders):
        self.encoders = encoders

    def serialize_request(self, httprequest):
        if hasattr(httprequest, "headers"):
            formatted_header = self.prepare_header(httprequest.headers)
            if "content-type" in formatted_header:
                contenttype = formatted_header["content-type"]
                enc = self._encoder(contenttype)
                if enc:
                    return enc.encode(httprequest)
                else:
                    raise IOError(
                        "Unable to serialize request with Content-Type {0}. Supported encodings are {1}".format(
                            contenttype, self.supported_encodings()))
        else:
            raise IOError("Http request does not have Content-Type header set")

    def deserialize_response(self, response_body, headers):
        formatted_headers = self.prepare_header(headers)
        if formatted_headers and "content-type" in formatted_headers:
            contenttype = formatted_headers["content-type"]
            enc = self._encoder(contenttype)
            if enc:
                return enc.decode(response_body)
            else:
                raise IOError(
                    "Unable to deserialize response with Content-Type {0}. Supported decodings are {1}".format(
                        contenttype, self.supported_encodings()))
        else:
            raise IOError("Http response does not have Content-Type header set")

    def prepare_header(self, headers):
        if headers:
            return dict((k.lower(), v) for k, v in headers.items())

    def supported_encodings(self):
        return [enc.content_type() for enc in self.encoders]

    def _encoder(self, content_type):
        for enc in self.encoders:
            if re.match(enc.content_type(), content_type) is not None:
                return enc
        return None
