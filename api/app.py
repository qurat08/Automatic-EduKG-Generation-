from flask import Flask, make_response, request
from werkzeug.datastructures import FileStorage
from flask_cors import CORS
from flask_restplus import Resource, Api
from exceptions.exceptions import PreprocessingException
from kwp_extraction.dbpedia.data_service import DataService

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

# parser = api.parser()
# parser.add_argument('file', type=FileStorage, location='files', required=True)
# parser.add_argument('model_name', type=str, location='args')
# parser.add_argument('material_id', type=str, location='args', required=True)


@api.route('/concept-map', endpoint='concept-map', methods=["POST"])
@api.doc(responses={200: 'Success', 400: "Validation Error"})
class PDFExctractorResource(Resource):

    def post(self):
        if request.method == "POST":
            model = request.form.get("model")
            materialId = request.form.get("materialId")
            materialName = request.form.get("materialName")
            materialFile = request.files.get("materialFile")

            print("model: ", model, "materialId:", materialId, "materialName:",
                  materialName, "file: ", materialFile)

            data_service = DataService()
            resp = data_service._get_data(materialId=materialId,
                                          materialName=materialName,
                                          file=materialFile,
                                          model_name=model,
                                          top_n=15,
                                          with_category=True,
                                          with_property=True,
                                          with_doc_sim=True)
            
            user={ "name":"user1", "id": "001" }
            concepts = [("Big data", 1),("Data model", 0),("Key-value database", 0)]
            data_service._construct_user(user, concepts)

            return make_response(resp, 200)


@api.errorhandler(PreprocessingException)
@api.errorhandler(Exception)
def handle_exception(error):
    return {'message': error.message}, 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
