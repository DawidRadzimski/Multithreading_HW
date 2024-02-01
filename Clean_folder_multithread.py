import os
import shutil
import zipfile
import rarfile
from concurrent.futures import ThreadPoolExecutor

# Słownik z kategoriami plików i odpowiadającymi im rozszerzeniami
file_categories = {
    'images': ('.jpeg', '.png', '.jpg', '.svg'),
    'videos': ('.avi', '.mp4', '.mov', '.mkv'),
    'documents': ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
    'music': ('.mp3', '.ogg', '.wav', '.amr'),
    'archives': ('.zip', '.gz', '.tar', '.rar')
}


# Funkcja do transliteracji polskich liter i zamiany innych znaków na '_'
def normalize(text):
    normalized_text = text
    normalized_text = normalized_text.replace('ą', 'a').replace('ę', 'e').replace('ż', 'z').replace('ć', 'c').replace(
        'ś', 's').replace('ź', 'z').replace('ń', 'n').replace('ł', 'l').replace('ó', 'o')
    normalized_text = normalized_text.replace('Ą', 'A').replace('Ę', 'E').replace('Ż', 'Z').replace('Ć', 'C').replace(
        'Ś', 'S').replace('Ź', 'Z').replace('Ń', 'N').replace('Ł', 'L').replace('Ó', 'O')
    normalized_text = ''.join(c if c.isalnum() or c.isspace() else '_' for c in normalized_text)
    return normalized_text


# Funkcja do przenoszenia i rozpakowywania archiwów
def move_and_extract_archive(source_path, target_dir):
    file_name, file_ext = os.path.splitext(source_path)

    if file_ext.lower() in ('.zip', '.gz', '.tar'):
        try:
            with zipfile.ZipFile(source_path, 'r') as zip_file:
                zip_file.extractall(target_dir)
            os.remove(source_path)  # Usuń archiwum ZIP po rozpakowaniu
        except zipfile.BadZipFile:
            pass
    elif file_ext.lower() == '.rar':
        try:
            with rarfile.RarFile(source_path, 'r') as rar_file:
                rar_file.extractall(target_dir)
            os.remove(source_path)  # Usuń archiwum RAR po rozpakowaniu
        except rarfile.NeedFirstVolume:
            pass


# Funkcja do sortowania plików
def organize_files(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            normalized_name = normalize(file_name)
            source_path = os.path.join(root, file)
            target_dir = None

            # Sprawdzanie rozszerzenia i wybieranie kategorii
            for category, extensions in file_categories.items():
                if file_ext.lower() in extensions:
                    target_dir = os.path.join(folder,
                                              category)  # Ustalamy folder kategorii na poziomie folderu docelowego
                    break

            # Jeśli kategoria nie została znaleziona, przenieś do "unknown"
            if target_dir is None:
                target_dir = os.path.join(folder, 'unknown')  # Ustalamy folder 'unknown' na poziomie folderu docelowego

            target_path = os.path.join(target_dir, normalized_name + file_ext)

            # Tworzenie kategorii, jeśli nie istnieje
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # Przeniesienie pliku (jeśli jeszcze nie istnieje w folderze docelowym)
            if not os.path.exists(target_path):
                shutil.move(source_path, target_path)

            # Rozpakowywanie archiwów (jeśli to archiwum)
            if file_ext.lower() in file_categories['archives']:
                move_and_extract_archive(target_path, target_dir)
                if os.path.exists(target_path):
                    os.remove(target_path)

        # Usuwanie pustych folderów
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)

def organize_files_multithreaded(folder):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(folder):
            for file in files:
                executor.submit(organize_file, root, file)  # Przeniesienie pliku do osobnego wątku

# Funkcja do wyświetlania raportu
def display_report(folder):
    categories = list(file_categories.keys()) + ['unknown']

    print("Kategorie plików:")
    for category in categories:
        category_path = os.path.join(folder, category)
        if os.path.exists(category_path):  # Sprawdź, czy kategoria istnieje
            file_list = os.listdir(category_path)
            print(f"- {category}: {len(file_list)} plików")

    known_extensions = set(ext for exts in file_categories.values() for ext in exts)
    unknown_extensions = set()

    for root, _, files in os.walk(folder):
        for file in files:
            _, file_ext = os.path.splitext(file)
            if file_ext not in known_extensions:
                unknown_extensions.add(file_ext)

    print("\nZnane rozszerzenia plików:")
    for ext in known_extensions:
        print(f"- {ext}")

    print("\nNierozpoznane rozszerzenia plików:")
    for ext in unknown_extensions:
        print(f"- {ext}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Użycie: python sort.py /ścieżka/do/folderu")
    else:
        folder_to_organize = sys.argv[1]
        organize_files(folder_to_organize)
        display_report(folder_to_organize)
        print("Sortowanie i organizacja zakończone.")
