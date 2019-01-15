import yaml


def read_yaml(file):
    with open(f"{file}.yaml", 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
