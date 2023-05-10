from pdfextractor.text_extractor import PDFTextExtractor

from kwp_extraction.dbpedia.concept_tagging import DBpediaSpotlight
from db.neo4_db import NeoDataBase
from kwp_extraction.model import KeyphraseExtractor
from exceptions.exceptions import PreprocessingException
import os

import logging
from log import LOG

logger = LOG(name=__name__, level=logging.DEBUG)

ALLOWED_EXTENSIONS = {'pdf'}


class DataService:

    def __init__(self):
        NEO4J_URI = os.environ.get('NEO4J_URI')
        NEO4J_USER = os.environ.get('NEO4J_USER')
        NEO4J_PASSWORD = os.environ.get('NEO4J_PW')

        self.db = NeoDataBase(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    def _construct_user(self, user, concepts):
        self.db.construct_user_model(user,concepts)

    def _get_data(self,
                  materialId,
                  materialName,
                  file,
                  model_name,
                  top_n=5,
                  with_category=True,
                  with_property=True,
                  with_doc_sim=True,
                  whole_text=False):
        """
        """
        if self.db.lm_exists(materialId):
            logger.info("Found learning material '%s" % materialId)
            concepts, relations = self.db.get_or_create_concepts_and_relationships(
                materialId, materialName, [])

            ser_data = get_serialized_data(concepts, relations)

            return ser_data
        else:
            logger.info("Could not find learning material '%s" % materialId)
            if file and is_file_allowed(file.filename):
                try:
                    pdf_extractor = PDFTextExtractor()
                    text = pdf_extractor.extract_text(file)

                    if not model_name or model_name == "":
                        extractor = KeyphraseExtractor()
                    else:
                        extractor = KeyphraseExtractor(
                            embedding_model=model_name)

                    keyphrases = extractor.extract_keyphrases(
                        text=text,
                        top_n=top_n,
                        use_doc_segmentation=True,
                        use_embedding_alignment=True)
                    dbpedia = DBpediaSpotlight()
                    nodes = dbpedia.build_path(materialId=materialId,
                                               text=text,
                                               keyphrases=keyphrases,
                                               with_category=with_category,
                                               with_property=with_property,
                                               with_doc_sim=with_doc_sim,
                                               whole_text=whole_text)

                    concepts, relations = self.db.get_or_create_concepts_and_relationships(
                        materialId, materialName, nodes)

                    ser_data = get_serialized_data(concepts, relations)

                    return ser_data
                except ValueError as e:
                    logger.error(
                        "%s is not a valid TransformerWordEmbeddings model" %
                        model_name)
                except Exception as e:
                    logger.error(
                        "Failed extracting graph data for material '%s' - %s" %
                        (materialId, e))
            else:
                logger.error("Could not process invalid file %s" % file)
                raise PreprocessingException(
                    "Invalid File. Please upload only %s file" %
                    ALLOWED_EXTENSIONS)


def get_serialized_data(concepts, relations):
    """
    """
    data = {}
    ser_concepts = []
    ser_realations = []

    for concept in concepts:
        c = {
            "name": concept["name"],
            "id": concept["id"],
            "weight": concept["weight"],
            "uri": concept["uri"],
            "type": concept["type"],
            "wikipedia": concept["wikipedia"],
            "abstract": concept["abstract"]
        }
        ser_concepts.append({'data': c})
    for relation in relations:
        r = {
            "type": relation["type"],
            "source": relation["source"],
            "target": relation["target"],
            "weight": relation["weight"]
        }
        ser_realations.append({"data": r})

    data["nodes"] = ser_concepts
    data["edges"] = ser_realations

    return data


def is_file_allowed(filename):
    return '.' in filename and filename.split(
        '.')[-1].lower() in ALLOWED_EXTENSIONS
