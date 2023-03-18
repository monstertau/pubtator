import subprocess
from typing import List
from temporalio import activity
from dataclasses import dataclass
import yaml
from yaml.loader import SafeLoader


@dataclass
class ExtractCustomInput:
    pmids: List[str]


@activity.defn(name="ExtractEntities")
async def extract_entities(params: ExtractCustomInput) -> str:
    # Open the file and load the file
    data = None
    with open('pubrunner.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        testYaml = [
            {
                'PUBMED_CUSTOM': {
                    "pmids": ','.join(params.pmids),
                    "format": "bioc",
                    "rename": "PUBMED"
                }
            }
        ]
        data['resources']['test'] = testYaml
    with open('pubrunner.yml', 'w') as file:
        documents = yaml.dump(data, file, sort_keys=False)
        # d = yaml.dump(data, f,  default_flow_style=False)

    command = ['pubrunner', '--test', '--clean', '.']
    print("Executing %s" % str(command))
    retval = subprocess.call(command)

    command = ['pubrunner', '--test', '.']
    print("Executing %s" % str(command))
    retval = subprocess.call(command)
    return f"Hello, {params}!"
