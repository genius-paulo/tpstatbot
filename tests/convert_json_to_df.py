import pandas as pd
import json
from pandas import json_normalize

def json_to_dataframe(json_data):
    # Нормализуем JSON для обработки вложенных данных
    df = json_normalize(json_data)
    
    return df

# Пример чтения данных из JSON-файла
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Пример использования
if __name__ == "__main__":
    # Укажите путь к вашему JSON файлу
    json_file_path = 'output.json'
    
    # Читаем данные из файла
    json_data = read_json_file(json_file_path)

    # Преобразуем JSON в DataFrame
    posts_df = json_to_dataframe(json_data)

    # Выводим результат
    posts_df.to_csv('posts.df.csv', index=False)