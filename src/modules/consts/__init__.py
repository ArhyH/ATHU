import os
import importlib

# Получаем все файлы *.py
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        module_name = file[:-3]
        importlib.import_module(f"{__package__}.{module_name}")
