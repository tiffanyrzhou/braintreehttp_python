import unittest
import os


from braintreehttp.encoder import Encoder

class GenericRequest:
    pass

class EncoderTest(unittest.TestCase):

    def test_Encoder_serialize_request_throwsWhenHeadersNone(self):
        req = GenericRequest()
        req.body = {
            "key": "value",
            "list": ["one", "two"]
        }

        try:
            Encoder().serialize_request(req)
        except Exception as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual("Http request does not have Content-Type header set", str(e))

    def test_Encoder_serialize_request_throwsWhenContentTypeNotJson(self):
        req = GenericRequest()
        req.body = {
            "key": "value",
            "list": ["one", "two"]
        }
        req.headers = {
            "Content-Type": "application/xml"
        }

        try:
            Encoder().serialize_request(req)
        except Exception as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual("Unable to serialize request with Content-Type application/xml. Supported encodings are ['application/json', 'text/.*', 'multipart/.*']", str(e))

    def test_Encoder_serialize_request_withJsonContentType_stringifysData(self):
        req = GenericRequest()
        req.body = {
            "key": "value",
            "list": ["one", "two"]
        }
        req.headers = {
            "Content-Type": "application/json"
        }

        j = Encoder().serialize_request(req)

        self.assertTrue('{' in j)
        self.assertTrue('"key": "value"' in j)
        self.assertTrue('"list": ["one", "two"]' in j)

    def test_Encoder_serialize_request_withTextContentType_stringifiesData(self):
        req = GenericRequest()
        req.body = "some text data"
        req.headers = {
            "Content-Type": "text/plain"
        }

        b = Encoder().serialize_request(req)

        self.assertEqual(req.body, b)

    def test_Encoder_serialize_request_withMultipartContentType_stringifysData(self):
        request = GenericRequest()
        request.path = "/"
        request.verb = "POST"
        request.headers = {"Content-Type": "multipart/form-data"}
        f = open(abspath('tests/resources/fileupload_test_binary.jpg'), 'rb')
        request.body = {"some_key": "some_value", "some_nested[key]": "some_nested_value", "file": f}

        file_data = f.read()

        serialized = Encoder().serialize_request(request)
        self.assertTrue("multipart/form-data; boundary=" in request.headers["Content-Type"])

        self.assertTrue("Content-Disposition: form-data; name=\"some_key\"" in serialized)
        self.assertTrue("some_value" in serialized)
        self.assertTrue("Content-Disposition: form-data; name=\"some_nested[key]\"" in serialized)
        self.assertTrue("some_nested_value" in serialized)
        self.assertTrue("Content-Disposition: form-data; name=\"file\"; filename=\"fileupload_test_binary.jpg\"" in serialized)
        self.assertTrue("Content-Type: image/jpeg" in serialized)
        self.assertTrue(str(f.read()) in serialized)

        f.close()

def abspath(path):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)

    def test_Encoder_deserialize_response_throwsWhenHeadersNone(self):
        j = '{"key": "value", "list": ["one", "two"]}'

        headers = None

        try:
            b = Encoder().deserialize_response(j, headers)
        except IOError as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual("Http response does not have Content-Type header set", str(e))

    def test_Encoder_deserialize_response_throwsWhenContentTypeNotJson(self):
        j = '{"key": "value", "list": ["one", "two"]}'

        headers = {"Content-Type": "application/xml"}

        try:
            b = Encoder().deserialize_response(j, headers)
        except IOError as e:
            self.assertIsInstance(e, IOError)
            self.assertEqual("Unable to deserialize response with Content-Type application/xml. Supported decodings are ['application/json', 'text/.*']", str(e))

    def test_Encoder_deserialize_response_text(self):
        j = 'some plain text'
        headers = {"Content-Type": "text/plain"}

        b = Encoder().deserialize_response(j, headers)

        self.assertEqual(j, b)

    def test_Encoder_deserialize_response_Json(self):
        j = '{"key": "value", "list": ["one", "two"]}'

        headers = {"Content-Type": "application/json"}

        b = Encoder().deserialize_response(j, headers)

        self.assertEqual("value", b["key"])
        self.assertEqual(["one", "two"], b["list"])

    def test_Encoder_deserialize_response_multipart(self):
        j = 'some plain text'
        headers = {"Content-Type": "multipart/form-data"}

        try:
            b = Encoder().deserialize_response(j, headers)
        except IOError as e:
            self.assertTrue('Multipart does not support deserialization', str(e))

        self.assertEqual(j, b)
