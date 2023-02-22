import argparse
import os
import sys
from enum import Enum

from bioc import biocxml
from mongoengine import *
from dotenv import load_dotenv

load_dotenv()
MONGO_DB = os.getenv('MONGO_DB')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PWD = os.getenv('MONGO_PWD')


class AnnotationType(Enum):
    Gene = 'GeneOrGeneProduct'
    Chemical = 'ChemicalEntity'
    Disease = 'DiseaseOrPhenotypicFeature'
    Mutation = 'SequenceVariant'


class PubmedAnnotation(EmbeddedDocument):
    kb_id = StringField(max_length=128)
    ann_type = EnumField(AnnotationType)
    start_offset = IntField()
    end_offset = IntField()
    ann_text = StringField(max_length=128)


class PubmedDocument(Document):
    pmid = StringField(max_length=20, primary_key=True)
    title = StringField()
    abstract = StringField()
    annotations = ListField(EmbeddedDocumentField(PubmedAnnotation))


def get_kb_id(ann_info):
    kbid = None
    if 'Chemical' in ann_info['type'] or 'Disease' in ann_info['type']:
        kbid = ann.infons.get('MESH')
    elif 'Gene' in ann_info['type']:
        kbid = ann.infons.get('NCBI Gene')
    elif 'Mutation' in ann_info['type']:
        kbid = ann.infons.get('Identifier')
    return kbid


def get_ann_type(ann_info):
    annotation_type = None
    if 'Chemical' in ann_info['type']:
        annotation_type = AnnotationType.Chemical
    elif 'Disease' in ann_info['type']:
        annotation_type = AnnotationType.Disease
    elif 'Gene' in ann_info['type']:
        annotation_type = AnnotationType.Gene
    elif 'Mutation' in ann_info['type']:
        annotation_type = AnnotationType.Mutation
    return annotation_type


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add processed data to database')
    parser.add_argument('--inBioc', required=True, type=str, help='Input BioC XML file')

    args = parser.parse_args()
    in_bioc = os.path.abspath(args.inBioc)

    assert os.path.isfile(in_bioc), "Could not access input: %s" % in_bioc
    if not os.path.getsize(in_bioc):
        sys.exit()
    input_file = open(in_bioc)
    input_data = biocxml.load(input_file)

    connect(MONGO_DB, host=MONGO_HOST, port=int(MONGO_PORT), username=MONGO_USER, password=MONGO_PWD)

    for document in input_data.documents:
        pubmed_doc = PubmedDocument(pmid=document.id)
        for passage in document.passages:
            if 'title' in passage.infons['section']:
                pubmed_doc.title = passage.text

            if 'abstract' in passage.infons['section']:
                pubmed_doc.abstract = passage.text

            for i, ann in enumerate(passage.annotations):
                kb_id = get_kb_id(ann.infons)
                if not kb_id:
                    continue
                pubmed_ann = PubmedAnnotation()
                pubmed_ann.kb_id = kb_id
                pubmed_ann.ann_type = get_ann_type(ann.infons)
                pubmed_ann.start_offset = ann.locations[0].offset
                pubmed_ann.end_offset = ann.locations[0].offset + ann.locations[0].length
                pubmed_ann.ann_text = ann.text

                pubmed_doc.annotations.append(pubmed_ann)
        pubmed_doc.update(upsert=True, add_to_set__annotations=pubmed_doc.annotations,
                          set__title=pubmed_doc.title, set__abstract=pubmed_doc.abstract)
