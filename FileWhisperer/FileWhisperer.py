from OperaPowerRelay import opr
import os
import traceback



"""

FileWhisperer

Serves to go through the contents of a folder, collect the metadata, then alter it

"""

AUDIO_FORMATS = [
    ".mp3",  # MPEG Audio Layer III
    ".wav",  # Waveform Audio File Format
    ".flac",  # Free Lossless Audio Codec
    ".opus",  # Opus Audio Codec
    ".aac",  # Advanced Audio Codec
    ".ogg",  # Ogg Vorbis
    ".m4a",  # MPEG-4 Audio
    ".wma",  # Windows Media Audio
    ".alac",  # Apple Lossless Audio Codec
    ".aiff",  # Audio Interchange File Format
    ".dsd",  # Direct Stream Digital
    ".amr",  # Adaptive Multi-Rate
    ".mp2",  # MPEG Audio Layer II
    ".mid",  # MIDI (Musical Instrument Digital Interface)
    ".caf",  # Core Audio Format (Apple)
]

IMAGE_FORMATS = [
    ".jpg",  # JPEG Image
    ".jpeg", # JPEG Image
    ".png",  # Portable Network Graphics
    ".gif",  # Graphics Interchange Format
    ".bmp",  # Bitmap Image
    ".tiff", # Tagged Image File Format
    ".tif",  # Tagged Image File Format
    ".webp", # WebP Image Format
    ".ico",  # Icon File
    ".svg",  # Scalable Vector Graphics
    ".heif", # High Efficiency Image Format
    ".heic", # High Efficiency Image Coding
    ".jp2",  # JPEG 2000
    ".jxl",  # JPEG XL
    ".psd",  # Adobe Photoshop Document
    ".xcf",  # GIMP Image Format
    ".dds",  # DirectDraw Surface (Texture Format)
    ".raw",  # Raw Image Data
    ".cr2",  # Canon RAW Image
    ".nef",  # Nikon RAW Image
    ".arw",  # Sony RAW Image
    ".dng",  # Digital Negative (Adobe RAW)
    ".orf",  # Olympus RAW Image
    ".rw2",  # Panasonic RAW Image
]

INVALID_CHARACTERS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

def get_version() -> str:
    return "1.1"

class CleanFile:
   
    """
    CleanFile

    This class is used to represent a file in the context of the FileWhisperer.
    It provides properties for the name and path of the file, as well as the
    metadata associated with the file.

    Parameters
    ----------
    name : str
        The name of the file.
    path : str
        The path to the file.
    provided : str
        The path to the folder or file that was provided to the FileWhisperer.

    Attributes
    ----------
    Name : str
        The name of the file.
    Path : str
        The path to the file.
    ProvidedPath : str
        The path to the folder or file that was provided to the FileWhisperer.
    RelativePath : str
        The relative path to the file from the provided folder or file.
    FullPath : str
        The full path to the file.
    Metadata : str
        The metadata associated with the file.
    """

    def __init__(self, name: str, path: str, provided: str) -> None:
        self._name = name
        self._original_name = name
        self._path = path
        self._original_path = path
        self._provided_path = provided
        self._metadata = get_metadata_omni(path)


    def __str__(self) -> str:
        return f"{self._name}"

    @property
    def Name(self) -> str:
        return self._name
    @Name.setter
    def Name(self, value: str):
        """
        Sets the name of the file, ensuring the correct file extension is preserved.
        Updates the file path accordingly.

        Parameters
        ----------
        value : str
            The new name for the file.
        """

        ext = os.path.splitext(self._path)[1]
        if not value.endswith(ext):
            value += ext

        for f in INVALID_CHARACTERS:
            if f in value:
                opr.print_from("FileWhisperer - CleanFile", f"Invalid character in file name: {f}. Removing...")
                value = value.replace(f, " ").strip()
                

        self._name = value

        dir_path = os.path.dirname(self._path)
        self._path = os.path.join(dir_path, self._name)

    @property
    def Path(self) -> str:
        return self._path
    @Path.setter
    def Path(self, value: str):
        self._path = value
    @property
    def ProvidedPath(self) -> str:
        return self._provided_path
    @property
    def RelativePath(self) -> str:
        return os.path.relpath(self._path, self._provided_path)
    @property
    def FullPath(self) -> str:
        return os.path.join(self.ProvidedPath, self.RelativePath)


    @property
    def Metadata(self) -> str:
        if self._metadata:
            return "\n".join(f"{key}: {value}" for key, value in self._metadata.items())
        else: 
            return f"{self._name} has no metadata"
            
    @property
    def Metadata_dict(self) -> dict[str, str]:
        return self._metadata or {}
    @Metadata_dict.setter
    def Metadata_dict(self, value: dict[str, str]):
        self._metadata = value

    def Save(self) -> None: 
        """
        Saves the metadata of a file. If the file's name has changed, the file is renamed to the new name.
        """
        
        _save_metadata(self)



def _save_metadata(file: CleanFile) -> bool:
    try:

        if file._original_path != file.Path:
            if os.path.exists(file.Path):
                opr.print_from("FileWhisperer - Save Metadata", f"FAILED: File already exists at {file.Path}")
                return False
            
            if not os.path.exists(os.path.dirname(file.Path)):
                os.rename(os.path.dirname(file._original_path), os.path.dirname(file.Path))
    
            
            old_name = os.path.join(os.path.dirname(file.Path), file._original_name)
            opr.print_from("FileWhisperer - Save Metadata", f"Renaming {old_name} to {file.Path}")
            os.rename(old_name, file.Path)
            file._original_name = file.Name
            file._original_path = file.Path

        if not _save_metadata_omni(file):
            opr.print_from("FileWhisperer - Save Metadata", f"FAILED: Failed to save metadata for {file.Name}")
            return False

        return True

    except Exception as e:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Save Metadata", f"FAILED: Unexpected error while saving metadata:\n{error_message}")
        return False
    
def _save_metadata_omni(file: CleanFile) -> bool:

    try:

        if any(file.Path.endswith(f) for f in AUDIO_FORMATS):
            return _save_audio_metadata(file)
        elif any(file.Path.endswith(f) for f in IMAGE_FORMATS):
            return _save_image_metadata(file)
        else:
            opr.print_from("FileWhisperer - Save Metadata Omni" , f"METADATA NOT AVAILABLE FOR: {file.Name}")
            return True

    except NotImplementedError:
        return True

    except Exception as e:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Save Metadata Omni", f"FAILED: Unexpected error while saving metadata:\n{error_message}")
        return False


def _save_audio_metadata(file: CleanFile) -> bool:
    import taglib
    try:
        audio = taglib.File(file.Path)
        if not audio:
            opr.print_from("FileWhisperer - Save Audio Metadata", f"UNSUPPORTED AUDIO FORMAT: {file.Name}")
            return False

        if file._metadata:
            for key, value in file.Metadata_dict.items():
                if value is not None:
                    audio.tags[key] = [value]

        audio.save() 
        audio.close() 

        opr.print_from("FileWhisperer - Save Audio Metadata", f"SUCCESS: Metadata saved for {file.Name}")
        return True

    except Exception as e:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Save Audio Metadata", f"FAILED: Unexpected error while saving metadata:\n{error_message}")
        return False

def _save_image_metadata(file: CleanFile) -> bool:
    """
    Saves the metadata of an image file.

    NOTE: I was too lazy to implement this as of version 1.1. Will implement it later

    This function takes a CleanFile object and attempts to save its metadata to the corresponding image file. If the file format is unsupported or an error occurs, it logs the error and returns False.

    Parameters
    ----------
    file : CleanFile
        The CleanFile object containing the metadata to be saved.

    Returns
    -------
    bool
        True if the metadata was saved successfully, False otherwise.
    """
    raise NotImplementedError


def display_files(files: list[CleanFile | dict[CleanFile, list]]):
    """
    Displays the contents of a list of CleanFile objects or dictionaries representing subdirectories.

    This function takes a list containing CleanFile objects or dictionaries representing subdirectories and prints the path, name, and metadata of each file to the console. If the element in the list is a dictionary, the function calls itself with the value of the dictionary, which is assumed to be a list of CleanFile objects or dictionaries.

    Parameters
    ----------
    files : list[CleanFile | dict[CleanFile, list]]
        A list containing CleanFile objects or dictionaries representing subdirectories.

    Returns
    -------
    None
    """
    for f in files:
        if isinstance(f, CleanFile):
            print(f"PATH: {f.Path}\nNAME: {f.Name}\nMETADATA:\n{f.Metadata}\n")
        elif isinstance(f, dict):
            display_files(f[list(f.keys())[0]])

def get_directory_contents(path: str, depth: int = 1) -> list[CleanFile | dict[str, list]]:
    """
    Enumerates the contents of a directory and returns a list of CleanFile objects or dictionaries representing subdirectories.

    This function takes a path to a directory and an optional depth parameter, and returns a list containing CleanFile objects for individual files or dictionaries for subdirectories. The function recursively processes nested directories to ensure all files and subdirectories are properly encapsulated.

    Parameters
    ----------
    path : str
        The path to the directory to be enumerated.
    depth : int, optional
        The maximum depth to which the directory should be enumerated. Defaults to 1.

    Returns
    -------
    list[CleanFile | dict[str, list]]
        A list containing CleanFile objects for individual files or dictionaries for subdirectories.
    """
    cleaned_path = _clean_path(path)
    files = opr.enumerate_directory(cleaned_path, depth)
    print(f"CLEANED PATH {cleaned_path}")
    return clean_files(files = files, path = cleaned_path, provided= cleaned_path)

def clean_files(files: list[str | dict[str, list]], path, provided) -> list[CleanFile | dict [str, list]]:
    """
    Takes a list of strings and dictionaries representing a directory structure and returns a list of CleanFile objects or dictionaries representing subdirectories.

    This function takes a list containing strings representing individual files and dictionaries representing subdirectories, and returns a list containing CleanFile objects for individual files or dictionaries for subdirectories. The function recursively processes nested directories to ensure all files and subdirectories are properly encapsulated.

    Parameters
    ----------
    files : list[str | dict[str, list]]
        A list containing strings representing individual files and dictionaries representing subdirectories.
    path : str
        The path to the current directory being processed.
    provided : str
        The path to the folder or file that was provided to the FileWhisperer.

    Returns
    -------
    list[CleanFile | dict[str, list]]
        A list containing CleanFile objects for individual files or dictionaries for subdirectories.
    """
    cleaned_files = []
    for f in files:
        if isinstance(f, str):            
            cleaned_files.append(CleanFile(name = f, path = os.path.join(path, f), provided=provided))

        elif isinstance(f, dict):
            subdirectory_name, subdirectory_items = next(iter(f.items()))
            cleaned_files.append({subdirectory_name: clean_files(subdirectory_items, os.path.join(path, subdirectory_name), provided) })
        else:
          raise Exception
        
    return cleaned_files

def get_audio_metadata(path: str) -> dict[str, str] | None:
    """
    Extracts and returns metadata from an audio file.

    This function utilizes the taglib library to read metadata from an audio file
    specified by the provided path. It retrieves the title, artist, album, and date
    of last modification of the audio file. If the file format is unsupported or an 
    error occurs during the process, it logs the error and returns None.

    Parameters
    ----------
    path : str
        The file path to the audio file from which metadata is to be extracted.

    Returns
    -------
    dict[str, str] | None
        A dictionary containing the audio metadata with keys 'TITLE', 'ARTIST', 'ALBUM', 
        and 'DATE'. Returns None if the file format is unsupported or an error occurs.
    """

    import taglib
    from datetime import datetime

    try:   
        audio = taglib.File(path)
        if not audio:
            opr.print_from("FileWhisperer - Get Audio Metadata", f"UNSUPPORTED AUDIO FORMAT: {os.path.basename(path)}")
            raise Exception
        
        metadata = {            
            "TITLE": audio.tags.get("TITLE", [os.path.basename(path)])[0],
            "ARTIST": audio.tags.get("ARTIST", ["Unknown"])[0],
            "ALBUM": audio.tags.get("ALBUM", ["Unknown"])[0],
            "DATE": audio.tags.get("DATE", [datetime.fromtimestamp(float(os.path.getmtime(path))).strftime("%Y-%m-%d %H:%M:%S")])[0],
        }

        opr.print_from("FileWhisperer - Get Audio Metadata", f"SUCCESS: Collected metadata for {os.path.basename(path)}")

        return metadata

    except Exception as e:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Get Audio Metadata", f"FAILED: Unexpected error while getting metadata:\n{error_message}")
        return None

def get_image_metadata(path: str) -> dict[str, str] | None:
    """
    Extracts and returns metadata from an image file using EXIF data.

    This function opens an image file specified by the given path and attempts
    to extract its metadata using the EXIF standard. The metadata is returned
    as a dictionary with tag names as keys and corresponding values. If the
    image does not contain EXIF data or if an error occurs, it logs the error
    and returns None.

    Parameters
    ----------
    path : str
        The file path to the image file from which metadata is to be extracted.

    Returns
    -------
    dict[str, str] | None
        A dictionary containing the image metadata with EXIF tag names as keys
        and their corresponding values. Returns None if the image does not 
        contain EXIF data or an error occurs during extraction.
    """

    from PIL import Image
    from PIL.ExifTags import TAGS
    import traceback
    import os

    metadata = {}
    try:
        img = Image.open(path)
        exif_data = img._getexif() 

        if exif_data is None:
            opr.print_from("FileWhisperer - Get Image Metadata", f"NO EXIF DATA: {os.path.basename(path)}")
            return None

        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag) 
            metadata[tag_name] = value

        opr.print_from("FileWhisperer - Get Image Metadata", f"SUCCESS: Collected metadata for {os.path.basename(path)}")
        return metadata

    except Exception as e:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Get Image Metadata", f"FAILED: Unexpected error while getting metadata:\n{error_message}")
        return None


def get_metadata_omni(path: str) -> dict[str, list] | None:
    """
    Attempts to extract metadata from a file using either audio or image metadata standards.

    This function takes a file path and attempts to extract its metadata using the
    appropriate standard (audio or image). If the file does not contain metadata
    or if an error occurs, it logs the error and returns None.

    NOTE: This is where you add more file types if you wish to support them

    Parameters
    ----------
    path : str
        The file path from which metadata is to be extracted.

    Returns
    -------
    dict[str, list] | None
        A dictionary containing the file metadata with tag names as keys
        and their corresponding values. Returns None if the file does not
        contain metadata or an error occurs during extraction.
    """
    path = _clean_path(path)
    if any(path.endswith(f) for f in AUDIO_FORMATS):
        return get_audio_metadata(path)
    if any(path.endswith(f) for f in IMAGE_FORMATS):
        return get_image_metadata(path)
    else:
        opr.print_from("FileWhisperer - Get Metadata Omni" , f"METADATA NOT AVAILABLE FOR: {os.path.basename(path)}")


def _get_all_metadata(files: list[CleanFile | dict[str, list]]) -> list[CleanFile, dict[str, list]] | None:
    
    """
    NOTE: Depreciated and shouldn't be used. Metadata collection is handled by the CleanFiles themselves

    Collects metadata from a list of CleanFile objects and dictionaries representing a directory structure.

    This function iterates over the input list and collects metadata from each CleanFile object and recursively
    from each dictionary representing a subdirectory. If a file format is unsupported or an error occurs during
    metadata extraction, it logs an error and continues with the next file.

    Parameters
    ----------
    files : list[CleanFile | dict[str, list]]
        A list of CleanFile objects and dictionaries representing the directory structure from which metadata is
        to be collected.

    Returns
    -------
    list[CleanFile, dict[str, list]] | None
        A list of dictionaries containing metadata for each file and subdirectory in the input list. Returns None
        if an error occurs during metadata extraction.
    """
    serialized_files = []

    for f in files:
        if isinstance(f, CleanFile):            
            opr.print_from("FileWhisperer - Get all metadata", f"Collecting metadata for {os.path.basename(f)}")
            _ = get_metadata_omni(f)
            if _ is not None:
                serialized_files.append(_)
        elif isinstance(f, list):
            opr.print_from("FileWhisperer - Get all metadata", f"Collecting metadata for directory {os.path.basename(f)}")
            _ = _get_all_metadata(f)
            if _ is not None:
                serialized_files.append(_)
        else: 
            opr.print_from("FileWhisperer - Get all metadata", f"Appending {f}. This shouldn't happen")
            serialized_files.append(f)

    return serialized_files

def _clean_path(path: str) -> str:
    """
    This method is obsolete and should not be used. Instead, use the one found in the OperaPowerRelay module.

    This method cleans a path by removing any leading or trailing quotes, and
    replacing any double quotes with single quotes.

    Parameters
    ----------
    path : str
        The path to be cleaned.

    Returns
    -------
    str
        The cleaned path.
    """
    if path.startswith("& "):
        path = path[2:]

    if (path.startswith("'") and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
        path = path[1:-1]

    if "''" in path:
        path = path.replace("''", "'")

    return os.path.normpath(path)

def rename_file(file: CleanFile, new_name) -> CleanFile:
    """
    Renames a CleanFile object.

    This function takes a CleanFile object and a new name, and renames the
    file. It also logs the success of the operation.

    Parameters
    ----------
    file : CleanFile
        The CleanFile object to be renamed.
    new_name : str
        The new name for the file.

    Returns
    -------
    CleanFile
        The renamed CleanFile object.
    """

    old_name = file.Name
    file.Name = new_name

    opr.print_from("FileWhisperer - Rename File", f"SUCCESS: Renamed {old_name} to {file.Name}")
    return file

def save_clean_files(files: list[CleanFile | dict [str, list]]) -> bool:

    """
    Recursively saves all CleanFile objects in the given list.

    This function takes a list of CleanFile objects and/or dictionaries representing
    subdirectories and saves all the CleanFile objects in the list. If the element
    in the list is a dictionary, the function calls itself with the value of the
    dictionary, which is assumed to be a list of CleanFile objects or dictionaries.

    Parameters
    ----------
    files : list[CleanFile | dict[str, list]]
        A list containing CleanFile objects or dictionaries representing subdirectories.

    Returns
    -------
    bool
        True if all files were successfully saved, False otherwise.
    """
    try:        
        for f in files:
            if isinstance(f, CleanFile):
                f.Save()
            elif isinstance(f, dict):
                subdirectory_name, subdirectory_items = next(iter(f.items()))
                save_clean_files(subdirectory_items)

        opr.print_from("FileWhisperer - Save Clean files", f"SUCCESS: Completed save of clean files")
        return True
    
    except Exception:
        error_message = traceback.format_exc()
        opr.print_from("FileWhisperer - Save Clean Files", f"FAILED: Unexpected Error while saving clean files: {error_message}")
        return False
    

def get_one_file(path: str) -> CleanFile:
    """
    Returns a CleanFile object representing the file at the given path.

    Parameters
    ----------
    path : str
        The path to the file.

    Returns
    -------
    CleanFile
        A CleanFile object representing the file at the given path.
    """
    
    path = _clean_path(path)
    file = CleanFile(os.path.basename(path), path, path)
    return file

if __name__ == "__main__":
# for testing purposes
    """
    opr.print_from("FileWhisperer", "Starting...")
    path = input("Path: ")
    depth = int(input("Depth: "))
    directory = get_directory_contents(path, depth)
    display_files(directory)
    """
    path = input("Enter: ")
    path = _clean_path(path)
    filename = os.path.basename(path)
    file = CleanFile(filename, path)
    print(file.Metadata_dict)
    """
    file.Save()
    print(f"Name: {file.Name}\nPath: {file.Path}")
    """
