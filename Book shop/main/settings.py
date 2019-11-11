import pathlib
import yaml

# Определение базовой директории
BASE_DIR = pathlib.Path(__file__).parent.parent
# Указание пути к файлу с настройками
config_path = BASE_DIR / 'config' / 'book.yaml'


# фунция получения настроек из файла с настройками
def get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


# Запуск функции с присвоением результата
config = get_config(config_path)
