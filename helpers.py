import json

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_categorical_options():
    return load_json('categoricals.json')

def load_scalar_traits():
    return load_json('scalars.json')

def load_tag_options():
    return load_json('tags.json')
