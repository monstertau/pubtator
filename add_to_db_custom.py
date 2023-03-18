import argparse
import os
import sys

from bioc import biocxml
from mongoengine import *
from dotenv import load_dotenv

from schema import AnnotationType, PubmedDocument, PubmedAnnotation

load_dotenv()
MONGO_DB = os.getenv('MONGO_DB')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PWD = os.getenv('MONGO_PWD')


def get_kb_id_pubtator(ann_info):
    kbids = None
    if 'Chemical' in ann_info['type'] or 'Disease' in ann_info['type']:
        identifier = ann_info.get('identifier', '')
        l_identifier = identifier.split(':')
        if len(l_identifier) > 1:
            kbids = [{'kb_type': l_identifier[0], 'kb_id': l_identifier[1]}]

    elif 'Gene' in ann_info['type']:
        ncbi_ids = ann_info.get('identifier', '')
        if len(ncbi_ids) > 0:
            kbids = [{'kb_type': 'NCBI Gene ID', 'kb_id': ncbi_ids}]

    elif 'Mutation' in ann_info['type']:
        identifiers = ann_info.get('identifier', '')
        l_identifier = identifiers.split(';')
        has_rs_id = False
        for kb_id in l_identifier:
            if 'RS' in kb_id.split(':')[0]:
                has_rs_id = True
        if has_rs_id:
            kbids = [{'kb_type': mut_kb_id.split(':')[0], 'kb_id': mut_kb_id.split(':')[1]} for mut_kb_id in
                     l_identifier]

    return kbids


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

    connect(MONGO_DB, host=MONGO_HOST, port=int(MONGO_PORT), username=MONGO_USER, password=MONGO_PWD,
            authentication_source=MONGO_DB)

    for document in input_data.documents:
        pubmed_doc = PubmedDocument(pmid=document.id)
        for passage in document.passages:
            if 'title' in passage.infons.get('section', '') or 'title' in passage.infons.get('type', ''):
                pubmed_doc.title = passage.text

            if 'abstract' in passage.infons.get('section', '') or 'abstract' in passage.infons.get('type', ''):
                pubmed_doc.abstract = passage.text

            for i, ann in enumerate(passage.annotations):
                kb_ids = get_kb_id_pubtator(ann.infons)
                if not kb_ids:
                    continue
                pubmed_ann = PubmedAnnotation(pmid=document.id)
                pubmed_ann.kb_ids = kb_ids
                pubmed_ann.ann_type = get_ann_type(ann.infons)
                pubmed_ann.start_offset = ann.locations[0].offset
                pubmed_ann.end_offset = ann.locations[0].offset + ann.locations[0].length
                pubmed_ann.ann_text = ann.text
                # pubmed_ann.update(upsert=True, set__kb_ids=pubmed_ann.kb_ids,
                #                   set__ann_text=pubmed_ann.ann_text,
                #                   set__ann_type=pubmed_ann.ann_type,
                #                   set__start_offset=pubmed_ann.start_offset,
                #                   set__end_offset=pubmed_ann.end_offset)
                pubmed_ann.save()
        # pubmed_doc.update(upsert=True, set__title=pubmed_doc.title, set__abstract=pubmed_doc.abstract)
        pubmed_doc.save()
