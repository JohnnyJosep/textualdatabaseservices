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
from pdf2image import convert_from_bytes

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


class OcrImageResponse(Schema):
    text = fields.String(default='')


class OcrPdfResponse(Schema):
    pages = fields.List(fields.String())



# def convert_pdf_to_images(store_pdfs_path, store_images_path):
#     if not os.path.isdir(store_images_path):
#         os.makedirs(store_images_path)
#     files = os.listdir(store_pdfs_path)
#     for file in files:
#         filename = file[0:-4]
#         pages_directory = f'{store_images_path}/{filename}'
#         if not os.path.isdir(pages_directory):
#             os.mkdir(pages_directory)
#         else:
#             continue

#         path = f'{store_pdfs_path}/{file}'
#         print(f'\tconverting {path}')
#         pages = convert_from_path(path)
#         for i in range(len(pages)):
#             pages[i].save(f'{pages_directory}/{filename}-PG-{i:03d}.jpeg', 'JPEG')


# def crop_images(store_images_path, store_crop_images_path):
#     if not os.path.isdir(store_crop_images_path):
#         os.mkdir(store_crop_images_path)

#     for directory in os.listdir(store_images_path):
#         print(f'\tcrop {directory}')
#         left = 175
#         top = 790
#         right = 1480
#         bottom = 2160
#         for image in sorted(os.listdir(f'{store_images_path}/{directory}')):
#             if not os.path.isdir(f'{store_crop_images_path}/{directory}'):
#                 os.mkdir(f'{store_crop_images_path}/{directory}')
#             else:
#                 continue

#             i = Image.open(f'{store_images_path}/{directory}/{image}')
#             i = i.crop((left, top, right, bottom))
#             path = f'{store_crop_images_path}/{directory}/{image}'
#             i.save(path, 'JPEG')

#             top = 296


class OcrTesseractImageAPI(MethodResource, Resource):

    @use_kwargs({'image': FileField(required=True)}, location='files')
    @marshal_with(OcrImageResponse)
    def post(self, image):
        if 'image' not in request.files:
            return 'Not file part', 400

        if image.filename == '':
            return 'No selected file', 400

        image_data = image.read()

        result = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)), lang='spa')
        return {'text': result}, 200


class OcrTesseractPdfAPI(MethodResource, Resource):

    @use_kwargs({'pdf': FileField(required=True)}, location='files')
    @marshal_with(OcrPdfResponse)
    def post(self, pdf):
        if 'pdf' not in request.files:
            return 'Not file part', 400

        if pdf.filename == '':
            return 'No selected file', 400

        pdf_data = pdf.read()
        pages = convert_from_bytes(pdf_data)

        pages_text = pytesseract.image_to_string(pages[0], lang='spa')
        return {'pages': [pages_text]}, 200


class HealthResponseSchema(Schema):
    success = fields.Boolean(default=True)
    message = fields.String(default='')


class HealthAPI(MethodResource, Resource):

    @doc(description='Health check.', tags=['health'])
    @marshal_with(HealthResponseSchema)
    def get(self):
        return {'success': True, 'message': "healthy"}


api.add_resource(HealthAPI, '/health')
api.add_resource(OcrTesseractImageAPI, '/ocr/image')
api.add_resource(OcrTesseractPdfAPI, '/ocr/pdf')
docs.register(HealthAPI)
docs.register(OcrTesseractImageAPI)
docs.register(OcrTesseractPdfAPI)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)