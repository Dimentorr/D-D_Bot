import json


class CatalogJson:
    def __init__(self, name: str):
        self.name = name
        with open(f'{name}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.json_data = data

    # second_key необходим на случай вложенного словаря в json и отвечает за название ключа в нём
    def update_json(self, data: dict, new_value: str, key: str, second_key='', name=''):
        if second_key != '':
            data[key][second_key] = new_value
        else:
            data[key] = new_value
        with open(f'{name}', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=3)

    def read_json_data(self, name_data):
        with open(f'{self.name}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[name_data]
