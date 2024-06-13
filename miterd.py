import os
import zipfile

import pandas as pd
from pandas import ExcelWriter
from unidecode import unidecode


def normalize_name(name, ext, max_length):
    """
    Normalize the file name by removing 'Propuesta_', spaces, accents, and limiting length.

    :param name: The original name of the file without extension.
    :param ext: The file extension.
    :param max_length: The maximum allowed length for the file name including the extension.
    :return: The normalized file name.
    """
    name = name.replace("Propuesta_", "").replace(" ", "")
    name = unidecode(name)[:max_length - len(ext)]
    return name + ext


def loop_miterd_criteria(main_folder, df_logs, depth, max_length=50):
    """
    Recursively check folders and files to apply criteria and log warnings or errors.

    :param main_folder: The main directory to start checking.
    :param df_logs: A dictionary containing DataFrames for logging errors and warnings.
    :param depth: The current depth of the directory structure being checked.
    :param max_length: The maximum allowed length for file names.
    :return: Updated dictionary with logs of errors and warnings.
    """
    folders = [os.path.join(main_folder, c) for c in os.listdir(main_folder)]

    for path in folders:

        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                with open(os.path.join(path, "leeme.txt"), mode="w", encoding="utf-8") as file:
                    file.write(u"En el envío no se adjuntó documentación")
            else:
                if depth > 4:
                    df_ = pd.DataFrame(
                        {
                            'description': ['Exceeded depth limit (depth > 4)'],
                            'value': [path]
                        })
                    df_logs['Warning'] = pd.concat([df_logs['Warning'], df_], axis=0)
                loop_miterd_criteria(path, df_logs, depth + 1)

        else:

            old_path = path
            path_, name = os.path.split(path)
            name, ext = os.path.splitext(name)
            name = normalize_name(name, ext, max_length)
            path = os.path.join(path_, name)

            if path != old_path:
                os.rename(old_path, unidecode(path))

            if ext in ['.zip', '.rar', '.gz']:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(path_)
                os.remove(path)

    return df_logs


def fix_miterd_folder_criteria(main_folder):
    """
    Check the main folder and apply criteria for files and subfolders.

    :param main_folder: The main directory to start checking.
    :return: DataFrames with logs of errors and warnings.
    """
    df_logs = \
        {
            'errors': pd.DataFrame(columns=['description', 'value']),
            'Warning': pd.DataFrame(columns=['description', 'value'])
        }

    # Llamada a la función recursiva comenzando desde el directorio principal con profundidad 1
    df_logs = loop_miterd_criteria(main_folder, df_logs=df_logs, depth=1)
    return df_logs


def save_logs_to_excel(logs, excel_file):
    """
    Save the logs to an Excel file.

    :param logs: The logs data to be saved.
    :param excel_file: The path to the Excel file.
    """
    with ExcelWriter(excel_file) as writer:
        logs['Warning'].to_excel(writer, sheet_name='Warnings', index=False)
        logs['errors'].to_excel(writer, sheet_name='Errors', index=False)
    print(f"Los datos se han guardado en el archivo '{excel_file}'.")


if __name__ == "__main__":
    folder_path = ".\\"
    logs = fix_miterd_folder_criteria(os.path.join(folder_path, 'Years', '2025-2030'))
    save_logs_to_excel(logs, "logs.xlsx")
