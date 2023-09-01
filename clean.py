from threading import Thread, Lock
import logging
import sys
from pathlib import Path
import uuid
import shutil
import re
from rich import print
import datetime

lock = Lock()


EXCEPTION = ["Audio", "Documents", "Images", "Video", "Archives", "Other"]

CATEGORIES = {
    "Audio": [".mp3", ".aiff", ".oog", ".wav", ".amr"],
    "Documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "Images": [".jpeg", ".png", ".jpg", ".svg"],
    "Video": [".avi", ".mp4", ".mov", ".mkv"],
    "Archives": [".zip", ".gz", ".tar"],
    "Other": [],
}
CYRILLIC_SYMBOLS = "абвгґдеёєжзиіїйклмнопрстуфхцчшщъыьэюя"
TRANSLATION = (
    "a",
    "b",
    "v",
    "h",
    "g",
    "d",
    "e",
    "e",
    "ie" "zh",
    "z",
    "y",
    "i",
    "yi",
    "y",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "u",
    "f",
    "kh",
    "ts",
    "ch",
    "sh",
    "shch",
    "",
    "y",
    "",
    "e",
    "yu",
    "ya",
)

BAD_SYMBOLS = ("%", "*", " ", "-")

TRANS = {}

dict_search_result = {}


def unpack_archive(item: Path, cat: Path):
    archive_name = item.stem
    output_dir = cat / archive_name
    output_dir.mkdir(exist_ok=True)

    shutil.unpack_archive(str(item), str(output_dir))


def delete_empty_folders(path):
    path = Path(path)
    if not path.is_dir():
        return

    for item in path.iterdir():
        if item.is_dir():
            delete_empty_folders(item)
    if not any(True for _ in path.iterdir()):
        path.rmdir()


def delete_arch_files(path):
    path = Path(path)

    if path.is_dir():
        for item in path.iterdir():
            delete_arch_files(item)

    if path.is_file() and path.suffix.lower() in (".zip", ".tar", ".gz"):
        path.unlink()


def file_list():
    lst = []
    longest_element = ""
    for category, value in dict_search_result.items():
        for element in value[0]:
            if len(element) > len(longest_element):
                longest_element = element
              
        ext = "Extensions: " + ", ".join(value[1]) 
        if len(ext) > len(longest_element):
            longest_element = ext

    oll_length = len(longest_element) + 2

    lst.append("|" + "=" * oll_length + "|")
    for category, value in dict_search_result.items():
        lst.append("|{:^{length}}|".format(str(category), length=oll_length))
        lst.append("|" + "=" * oll_length + "|")
        ext = "Extensions: "
        for extension in value[1]:
            ext += re.sub("\.", "", extension) + ", "
        ext = ext[:-2]
        lst.append("|{:<{length}}|".format(ext, length=oll_length))
        lst.append("|" + "-" * oll_length + "|")
        for element in value[0]:
            lst.append("|{:<{length}}|".format(element, length=oll_length))
        lst.append("|" + "=" * oll_length + "|")
    for i in lst:
        print(i)

    return lst


def normalize(name: str) -> str:
    for c, t in zip(list(CYRILLIC_SYMBOLS), TRANSLATION):
        TRANS[ord(c)] = t
        TRANS[ord(c.upper())] = t.upper()

    for i in BAD_SYMBOLS:
        TRANS[ord(i)] = "_"

        trans_name = name.translate(TRANS)
    return trans_name


def move_file(file: Path, root_dir: Path, categorie: str) -> None:
    ext = set()
    global dict_search_result
    target_dir = root_dir.joinpath(categorie)
    if not target_dir.exists():
        # print(f"Creation {target_dir}") # друкує теку яку сортуємо
        try:
            target_dir.mkdir()
        except FileExistsError:
            pass

    if file.suffix.lower() in (".zip", ".tar", ".gz"):
        try:
            unpack_archive(file, target_dir)
        except shutil.ReadError:
            return

    new_name = target_dir.joinpath(f"{normalize(file.stem)}{file.suffix}")
    if new_name.exists():
        new_name = new_name.with_name(f"{new_name.stem}-{uuid.uuid4()}{file.suffix}")
    with lock:
        file.rename(new_name)
    ext.add(file.suffix)

    with lock:
        if categorie in dict_search_result:
            dict_search_result[categorie][0].append(new_name.name)
            dict_search_result[categorie][1].update(ext)
        else:
            dict_search_result[categorie] = [[new_name.name], ext]


def get_categories(file: Path) -> str:
    ext = file.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Other"


def sort_folder(path: Path) -> None:
    threads = []

    def create_thread(item, path):
        cat = get_categories(item)
        move_f = Thread(target=move_file, args=(item, path, cat))
        threads.append(move_f)

    for item in path.glob("**/*"):
        logging.debug(f'{item}')
        if item.is_dir() and item.name in EXCEPTION:
            continue
        if item.is_file():
            create_thread(item, path)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()   


def save_log(list):
    # absolute_path = os.path.abspath(sys.argv[1])
    path = Path(sys.path[0]).joinpath("List_of_files.txt")
    with open(path, "w") as file:
        file.writelines(str(item) + "\n" for item in list)


def main(argv):
    try:
        path = Path(argv)
    except IndexError:
        return "No folder specified for sorting"
    if not path.exists():
        return f"This {path} does not exist."
    sort_folder(path)
    delete_empty_folders(path)
    delete_arch_files(path)
    # file_list()
    save_log(file_list())
    return f"The folder {path} is sorted - [bold green]success[/bold green]"


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    logging.basicConfig(level=logging.INFO, handlers=[
        logging.FileHandler("Sort_Log.txt")
        # logging.StreamHandler()
    ], format="%(asctime)s %(message)s")
    try:
        print(main(sys.argv[1]))
    except IndexError:
        print("Write path!")
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    logging.info(f'The job is done in: {execution_time}sec.')
    print(f'The job is done in: {execution_time}sec.')
