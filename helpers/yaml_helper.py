import yaml


def read_yaml(file):
    with open(f"{file}.yaml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def save_to_yaml(file, data):
    with open(f"{file}.yaml", 'w') as file:
        try:
            return yaml.safe_dump(data, file, sort_keys=False)
        except yaml.YAMLError as err:
            print(err)
            exit(1)
