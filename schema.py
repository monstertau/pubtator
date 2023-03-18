from enum import Enum

from mongoengine import *


class AnnotationType(Enum):
    Gene = 'GeneOrGeneProduct'
    Chemical = 'ChemicalEntity'
    Disease = 'DiseaseOrPhenotypicFeature'
    Mutation = 'SequenceVariant'


class PubmedDocument(Document):
    pmid = StringField(max_length=20)
    title = StringField()
    abstract = StringField()
    meta = {
        'indexes': [
            'pmid',
        ]
    }


class PubmedAnnotation(Document):
    pmid = StringField(max_length=20)
    kb_ids = ListField(DictField())
    ann_type = EnumField(AnnotationType)
    start_offset = IntField()
    end_offset = IntField()
    ann_text = StringField(max_length=128)
    # document = ReferenceField(PubmedDocument, reverse_delete_rule=CASCADE)
    meta = {
        'indexes': [
            'pmid',
            'ann_type',
            ('pmid', 'ann_type'),
        ]
    }
