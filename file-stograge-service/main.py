import uuid
import os

from flask import Flask, request, send_file
from flask_restful import Resource, Api
from apispec import APISpec
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

root_folder = os.environ['TFG_ROOT_FOLDER'] if 'TFG_ROOT_FOLDER' in os.environ else f'{os.path.abspath(os.getcwd())}/../.docker/fs'

file_plugin = MarshmallowPlugin()

app = Flask(__name__)
api = Api(app)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='File System Project',
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


class FileUploadResponseSchema(Schema):
    filename = fields.String(default='')


class HealthResponseSchema(Schema):
    success = fields.Boolean(default=True)
    message = fields.String(default='')


class HealthAPI(MethodResource, Resource):

    @doc(description='Health check.', tags=['health'])
    @marshal_with(HealthResponseSchema)
    def get(self):
        return {'success': True, 'message': "healthy"}


class FileSystemAPI(MethodResource, Resource):

    @doc(description='Get file.', tags=['fs'])
    def get(self, filename):
        path = os.path.join(root_folder, filename)

        if not os.path.isfile(path):
            return f'Not found ({filename})', 404

        return send_file(path)

    @doc(description='Delete file.', tags=['fs'])
    @marshal_with(None, code=204)
    def delete(self, filename):
        path = os.path.join(root_folder, filename)

        if not os.path.isfile(path):
            return f'Not found ({filename})', 404

        os.remove(path)
        return None, 204


class FileSystemStorageAPI(MethodResource, Resource):

    @use_kwargs({'file': FileField(required=True)}, location='files')
    @marshal_with(FileUploadResponseSchema, code=201)
    def post(self, file):
        if 'file' not in request.files:
            return 'Not file part', 400

        if file.filename == '':
            return 'No selected file', 400

        if file and file.filename.lower().endswith('.pdf'):
            guid = str(uuid.uuid4())
            filename = f'{guid}.pdf'

            file.save(os.path.join(root_folder, filename))

            return {'filename': filename}, 201

        else:
            return 'Not allowed file extension', 400


api.add_resource(HealthAPI, '/health')
api.add_resource(FileSystemStorageAPI, '/fs')
api.add_resource(FileSystemAPI, '/fs/<filename>')

docs.register(HealthAPI)
docs.register(FileSystemStorageAPI)
docs.register(FileSystemAPI)

if __name__ == '__main__':
    if not os.path.isdir(root_folder):
        os.mkdir(root_folder)

    app.run(host='0.0.0.0', port=80)
