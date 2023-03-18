import argparse
import os
import sys
from enum import Enum

from bioc import biocxml
from mongoengine import *
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
MONGO_DB = os.getenv('MONGO_DB')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PWD = os.getenv('MONGO_PWD')


class PubmedRelation(Document):
    pmid = StringField(max_length=20)
    first_kb_id = StringField()
    second_kb_id = StringField()
    relation_type = StringField()
    meta = {
        'indexes': [
            'pmid',
            'first_kb_id',
            'second_kb_id'
        ]
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add processed data to database')
    parser.add_argument('--relation_file', type=str, default='relation_full_new.out')
    args = parser.parse_args()

    rel = os.path.abspath(args.relation_file)

    assert os.path.isfile(rel), "Could not access input: %s" % rel
    d = {}
    with open(rel, 'r') as infile:
        for line in tqdm(infile):
            line = line.strip().split('\t')
            v = d.get(line[0], None)
            if not v:
                d[line[0]] = [[line[1], line[2], line[3]]]
            else:
                d[line[0]] += [[line[1], line[2], line[3]]]

    connect(MONGO_DB, host=MONGO_HOST, port=int(MONGO_PORT), username=MONGO_USER, password=MONGO_PWD,
            authentication_source=MONGO_DB)
    for pmid, relations in tqdm(d.items(), desc='Save relation to mongodb...'):
        PubmedRelation.objects(pmid=pmid).delete()
        for relation in relations:
            relation_obj = PubmedRelation(pmid=pmid, first_kb_id=relation[0],
                                          second_kb_id=relation[1], relation_type=relation[2])
            relation_obj.save()
