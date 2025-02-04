# create_workbench.py
import os
import json
from ruamel.yaml import YAML
from typing import Dict, Any

def load_datamodel(file_type: str, plugin_name: str) -> Dict[str, Any]:
    """Wczytuje plik JSON z datamodels i zwraca właściwości."""
    datamodel_path = f"{dirs(plugin_name)}/datamodels/conf.system.{file_type}.{plugin_name}.json"
    try:
        with open(datamodel_path, 'r') as f:
            data = json.load(f)
            return data.get('properties', {})
    except FileNotFoundError:
        print(f"Błąd: Plik {datamodel_path} nie istnieje!")
        return {}
    except json.JSONDecodeError:
        print(f"Błąd: Nieprawidłowy format pliku {datamodel_path}!")
        return {}

def map_field_type(json_type: str) -> str:
    """Mapuje typy JSON Schema na typy pól formularza."""
    type_mapping = {
        "string": "textInput",
        "boolean": "checkbox",
        "integer": "numberInput",
        "number": "numberInput"
    }
    return type_mapping.get(json_type, "textInput")

def create_component(file_type: str, plugin_name: str, properties: Dict[str, Any]):
    """Tworzy plik YAML dla komponentu."""
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    component_data = {
        "version": "1.0",
        "type": "component",
        "data": {
            "name": f"omv-{file_type}-{plugin_name}-index-form-page",
            "type": "formPage",
            "config": {
                "request": {
                    "service": plugin_name,
                    "get": {"method": "getSettings"},
                    "post": {"method": "setSettings"}
                },
                "fields": [],
                "buttons": [
                    {"template": "submit"},
                    {
                        "template": "cancel",
                        "execute": {
                            "type": "url",
                            "url": f"/services/{plugin_name}"
                        }
                    }
                ]
            }
        }
    }

    component_navigation_data = {
        "version": "1.0",
        "type": "component",
        "data": {
          "name": f"omv-{file_type}-{plugin_name}-navigation-page",
          "type": "navigationPage"
        }
    }

    navigation_data = {
        "version": "1.0",
        "type": "navigation-item",
        "data": {
          "path": f"{file_type}.{plugin_name}",
          "position": 15,
          "text": f'_("{plugin_name}")',
          "icon": "mdi:lan-connect",
          "url": f"/{file_type}/{plugin_name}"
        }
    }

    # Dodaj pola z właściwości JSON
    for field_name, props in properties.items():
        field_config = {
            "type": map_field_type(props.get('type', 'string')),
            "name": field_name,
            "label": f'_("{field_name.replace("_", " ").title()}")',
            "value": True
        }
        if 'description' in props:
            field_config['tooltip'] = f'_("{props["description"]}")'
        component_data['data']['config']['fields'].append(field_config)

    # Zapis pliku komponentu
    component_filename = f"{dirs(plugin_name)}/workbench/component.d/omv-{file_type}-{plugin_name}-index-form-page.yaml"
    component_navigation_filename = f"{dirs(plugin_name)}/workbench/component.d/omv-{file_type}-{plugin_name}-navigation-page.yaml"
    navigation_filename = f"{dirs(plugin_name)}/workbench/navigation.d/{file_type}.{plugin_name}.yaml"
    with open(component_filename, 'w') as f:
        yaml.dump(component_data, f)
    with open(component_navigation_filename, 'w') as f:
        yaml.dump(component_navigation_data, f)
    with open(navigation_filename, 'w') as f:
        yaml.dump(navigation_data, f)
    
    print(f"Utworzono plik komponentu: {component_filename}")

def dirs(plugin_name):
    plugin_dir = f"openmediavault-{plugin_name}"
    usr_dir = os.path.join(plugin_dir, "usr")
    omv_dir = os.path.join(usr_dir, "share", "openmediavault")
    return omv_dir

def create_workbench_structure(plugin_name,file_type):
    """Tworzy strukturę workbench i generuje pliki."""
    # Wczytanie właściwości z pliku JSON
    properties = load_datamodel(file_type, plugin_name)
    if not properties:
        return

    # Generowanie pliku komponentu
    create_component(file_type, plugin_name, properties)

if __name__ == "__main__":
    print("Tworzenie struktury workbench:")
    create_workbench_structure()