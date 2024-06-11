import os
import uuid

def rename_folders_to_uuid(path):
    # Listar todas las carpetas en el directorio especificado
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    # Renombrar las carpetas con nuevos UUID
    for folder in folders:
        old_folder_path = os.path.join(path, folder)
        new_uuid = str(uuid.uuid4())
        new_folder_path = os.path.join(path, new_uuid)

        # Verificar si ya existe una carpeta con el nuevo UUID (poco probable)
        if not os.path.exists(new_folder_path):
            os.rename(old_folder_path, new_folder_path)
            print(f"Renamed '{folder}' to '{new_uuid}'")
        else:
            print(f"Skipping '{folder}' as '{new_uuid}' already exists")

if __name__ == "__main__":
    folder_path = ".\\Years\\2025-2030\\2030"  # Especificar la ruta del directorio que contiene las carpetas
    rename_folders_to_uuid(folder_path)
