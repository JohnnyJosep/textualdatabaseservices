import pytesseract
from PIL import Image
import io
from flask import Flask, request
from flask_restful import Resource, Api
from apispec import APISpec
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

file_plugin = MarshmallowPlugin()
app = Flask(__name__)
api = Api(app)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='OCR Tesseract Project',
        version='v1',
        plugins=[file_plugin],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)


@file_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass


class OcrResponse(Schema):
    text = fields.String(default='')


class OcrTesseractAPI(MethodResource, Resource):

    @use_kwargs({'image': FileField(required=True)}, location='files')
    @marshal_with(OcrResponse)
    def post(self, image):
        if 'image' not in request.files:
            return 'Not file part', 400

        if image.filename == '':
            return 'No selected file', 400

        image_data = image.read()

        result = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)), lang='spa')
        return {'text': result}, 200


class HealthResponseSchema(Schema):
    success = fields.Boolean(default=True)
    message = fields.String(default='')


class HealthAPI(MethodResource, Resource):

    @doc(description='Health check.', tags=['health'])
    @marshal_with(HealthResponseSchema)
    def get(self):
        return {'success': True, 'message': "healthy"}


api.add_resource(HealthAPI, '/health')
api.add_resource(OcrTesseractAPI, '/ocr')
docs.register(HealthAPI)
docs.register(OcrTesseractAPI)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)