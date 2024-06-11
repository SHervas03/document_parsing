import os
import pandas as pd
from pandas import ExcelWriter
from unidecode import unidecode


# Función recursiva para iterar a través de los directorios y aplicar ciertos criterios
def loop_miterd_criteria(main_folder, df_logs, depth, max_length = 50):

    # Inicialización de los DataFrames de errores y advertencias si no se han inicializado
    if df_logs is None:
        df_logs = {
            'errors': pd.DataFrame(columns=['description', 'value']),
            'Warning': pd.DataFrame(columns=['description', 'value'])
        }

    # Obtención de la lista de rutas completas de todos los elementos en el directorio principal
    folders = [os.path.join(main_folder, c) for c in os.listdir(main_folder)]

    # Diccionario para contar los archivos con el mismo nombre
    file_count = {}

    # Iteración a través de cada ruta en la lista
    for path in folders:

        # Si la ruta es un directorio
        if os.path.isdir(path):
            # Si el directorio está vacío
            if len(os.listdir(path)) == 0:
                # Creación de un archivo "leeme.txt" indicando que no se adjuntó documentación
                with open(os.path.join(path, "leeme.txt"), mode="w", encoding="utf-8") as file:
                    file.write(u"En el envío no se adjuntó documentación")
            else:
                if depth > 1:
                    df_ = pd.DataFrame(
                        {
                            'description': ['Exceeded depth limit (depth > 4)'],
                            'value': [path]
                        })
                    df_logs['Warning'] = pd.concat([df_logs['Warning'], df_], axis=0)
                # Llama recursivamente a la función para iterar dentro del subdirectorio, incrementando la profundidad
                loop_miterd_criteria(path, df_logs, depth + 1)

        # Si la ruta no es un directorio (es un archivo)
        elif not os.path.isdir(path):

            path_ = os.path.dirname(path)
            old_path = path
            name, ext = os.path.splitext(os.path.basename(path))

            if name in file_count:
                file_count[name] += 1
                path = os.path.join(path_, name[:max_length - len(ext) - file_count[name] - 1] + "_" + str(file_count[name]) + ext)
            else:
                file_count[name] = 0
                path = os.path.join(path_, name[:max_length - len(ext)] + ext)
            os.rename(old_path, unidecode(path))
            old_path = path

            if ext in ['.doc', '.dotx', '.dotm', '.dot', '.docm', '.docb', '.rtf', '.odt', '.wps']:
                pass
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp']:
                pass
            elif ext in ['.lnk']:
                os.remove(path)
            elif ext in ['.xls', '.xlsm']:
                pass
            elif ext in ['.pdf', '.txt', '.docx', '.xlsx']:
                pass
            else:
                df_ = pd.DataFrame(
                    {
                        'description': ['Not file extension found'],
                        'value': [path]
                    })
                df_logs['Warning'] = pd.concat([df_logs['Warning'], df_], axis=0)

    return df_logs


# Función para iniciar el proceso en el directorio principal
def fix_miterd_folder_criteria(main_folder):

    # Inicialización de los DataFrames de errores y advertencias
    df_logs = \
        {
            'errors': pd.DataFrame(columns=['description', 'value']),
            'Warning': pd.DataFrame(columns=['description', 'value'])
        }

    # Llamada a la función recursiva comenzando desde el directorio principal con profundidad 1
    df_logs = loop_miterd_criteria(main_folder, df_logs=df_logs, depth=1)
    return df_logs


if __name__ == "__main__":
    folder_path = ".\\"
    logs = fix_miterd_folder_criteria(os.path.join(folder_path, 'Years', '2025-2030'))

    # Guardar los datos en un archivo Excel
    excel_file = 'logs.xlsx'
    with ExcelWriter(excel_file) as writer:
        logs['Warning'].to_excel(writer, sheet_name='Warnings', index=False)
        logs['errors'].to_excel(writer, sheet_name='Errors', index=False)
    print(f"Los datos se han guardado en el archivo '{excel_file}'.")
