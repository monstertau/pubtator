import argparse
import os
import sys

from bioc import biocxml
import bioc

from filter import filter_cancer_ann


def filter_gene_drug_var_ann(input_bioc):
    contain_doc = []
    for doc in input_bioc.documents:
        has_drug_ann = False
        has_gene_mut_ann = False
        for passage in doc.passages:
            for ann in passage.annotations:
                if 'Gene' in ann.infons['type'] or 'Mutation' in ann.infons['type']:
                    has_gene_mut_ann = True
                elif 'Chemical' in ann.infons['type']:
                    has_drug_ann = True
            if has_gene_mut_ann and has_drug_ann:
                contain_doc.append(doc)
                break
    input_bioc.documents = contain_doc


def process(input_bioc, output_path, filter_type):
    filter_ann = filter_cancer_ann if filter_type == 'cancerAnnotation' else filter_gene_drug_var_ann
    filter_ann(input_bioc)
    if not input_bioc.documents:
        return
    with open(output_path, 'w') as fp:
        bioc.dump(input_data, fp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter out relevant pubmed document')
    parser.add_argument('--type', required=True, type=str, help='filter type')
    parser.add_argument('--inBioc', required=True, type=str, help='Input BioC XML file')
    parser.add_argument('--outBioc', required=True, type=str, help='Output BioC XML file after filter')

    args = parser.parse_args()

    accepted_type = ['cancerAnnotation', 'geneDrugVarAnnotation']

    assert args.type in accepted_type, "--type must be %s" % str(accepted_type)

    in_bioc = os.path.abspath(args.inBioc)
    out_bioc = os.path.abspath(args.outBioc)

    assert os.path.isfile(in_bioc), "Could not access input: %s" % in_bioc
    if not os.path.getsize(in_bioc):
        sys.exit()
    input_file = open(in_bioc)

    input_data = biocxml.load(input_file)

    process(input_data, out_bioc, args.type)
