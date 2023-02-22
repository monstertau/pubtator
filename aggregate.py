import argparse
import os
import sys

import bioc
from bioc import biocxml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate NER result into one')
    parser.add_argument('--input', required=True, type=str, help='Input BioC XML file')
    parser.add_argument('--outTmChem', required=True, type=str, help='Output BioC XML tmChem file')
    parser.add_argument('--outDNorm', required=True, type=str, help='Output BioC XML DNorm file')
    parser.add_argument('--outGNorm', required=True, type=str, help='Output BioC XML GNorm file')
    parser.add_argument('--outTmVar', required=True, type=str, help='Output BioC XML TmVar file')
    parser.add_argument('--output', required=True, type=str, help='Output BioC XML aggregate file')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'cant find input file: {args.input}')
        exit(0)
    if not os.path.exists(args.outTmChem):
        print(f'cant find input file: {args.outTmChem}')
        exit(0)
    if not os.path.exists(args.outDNorm):
        print(f'cant find input file: {args.outDNorm}')
        exit(0)
    if not os.path.exists(args.outGNorm):
        print(f'cant find input file: {args.outGNorm}')
        exit(0)
    if not os.path.exists(args.outTmVar):
        print(f'cant find input file: {args.outTmVar}')
        exit(0)

    if not os.path.exists('/'.join(args.output.split('/')[:-1])):
        os.makedirs('/'.join(args.output.split('/')[:-1]))
    if not os.path.getsize(args.outDNorm) and not os.path.getsize(args.outGNorm) \
            and not os.path.getsize(args.outTmChem) and not os.path.getsize(args.outTmVar): # not in cancer list
        sys.exit()
    input_file = open(args.input)
    out_dnorm = open(args.outDNorm)
    out_gnorm = open(args.outGNorm)
    out_tmchem = open(args.outTmChem)
    out_tmvar = open(args.outTmVar)

    input_data = biocxml.load(input_file)
    tmchem_data = biocxml.load(out_tmchem)
    dnorm_data = biocxml.load(out_dnorm)
    gnorm_data = biocxml.load(out_gnorm)
    tmvar_data = biocxml.load(out_tmvar)
    x = 0
    for i, doc in enumerate(input_data.documents):
        for j, passage in enumerate(doc.passages):
            passage.annotations.extend(tmchem_data.documents[i].passages[j].annotations)
            passage.annotations.extend(dnorm_data.documents[i].passages[j].annotations)
            passage.annotations.extend(gnorm_data.documents[i].passages[j].annotations)
            passage.annotations.extend(tmvar_data.documents[i].passages[j].annotations)
            passage.annotations.sort(key=lambda t: t.locations[0].offset, reverse=False)
            for y, ann in enumerate(passage.annotations):
                ann.id = str(x)
                passage.annotations[y] = ann
                x += 1
            doc.passages[j] = passage

    with open(args.output, 'w') as fp:
        bioc.dump(input_data, fp)
