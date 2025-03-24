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


class CleanFile:
    def __init__(self, name: str, path: str) -> None:
        self._name = name
        self._original_name = name
        self._path = path
        self._original_path = path
        self._metadata = get_metadata_omni(path)

    def __str__(self) -> str:
        return f"{self._name}"

    @property
    def Name(self) -> str:
        return self._name
    @Name.setter
    def Name(self, value: str):
        ext = os.path.splitext(self._path)[1]
        if not value.endswith(ext):
            value += ext
        self._name = value

        dir_path = os.path.dirname(self._path)
        self._path = os.path.join(dir_path, self._name)

    @property
    def Path(self) -> str:
        return self._path
    
    @property
    def Metadata(self) -> str:
        return "\n".join(f"{key}: {value}" for key, value in self._metadata.items()) or f"{self._name} has no metadata"
        
    @property
    def Metadata_dict(self) -> dict[str, str]:
        return self._metadata or {}
    @Metadata_dict.setter
    def Metadata_dict(self, value: dict[str, str]):
        self._metadata = value

    def Save(self) -> None: _save_metadata(self)



def _save_metadata(file: CleanFile) -> bool:

    try:

        if file._original_path != file.Path:
            if os.path.exists(file.Path):
                opr.print_from("FileWhisperer - Save Metadata", f"FAILED: File already exists at {file.Path}")
                return False
            
            os.rename(file._original_path, file.Path)
            opr.print_from("FileWhisperer - Save Metadata", f"SUCCESS: Renamed {file._original_name} to {file.Name}")
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
        if any(file.Path.endswith(f) for f in IMAGE_FORMATS):
            return _save_image_metadata(file)
        else:
            opr.print_from("FileWhisperer - Save Metadata Omni" , f"METADATA NOT AVAILABLE FOR: {file.Name}")
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
    return _save_metadata(file)

def _display_files(files: list[CleanFile | dict[CleanFile, list]]):
    for f in files:
        if isinstance(f, CleanFile):
            print(f"PATH: {f.path}\nNAME: {f.name}\nMETADATA:\n{f.get_metadata}\n")
        elif isinstance(f, dict):
            _display_files(f[list(f.keys())[0]])

def _get_directory_contents(path: str, depth: int = 1) -> list[CleanFile | dict[str, list]]:
    files = opr.enumerate_directory(path, depth)
    return clean_files(files, path)

def clean_files(files: list[str | dict[str, list]], path) -> list[CleanFile | dict [str, list]]:
    cleaned_files = []
    for f in files:
        if isinstance(f, str):            
            cleaned_files.append(CleanFile(name = f, path = os.path.join(path, f)))

        elif isinstance(f, dict):
            subdirectory_name, subdirectory_items = next(iter(f.items()))
            cleaned_files.append({subdirectory_name: clean_files(subdirectory_items, os.path.join(path, subdirectory_name))})
        else:
          raise Exception
        
    return cleaned_files

def get_audio_metadata(path: str) -> dict[str, str] | None:
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
    path = clean_path(path)
    if any(path.endswith(f) for f in AUDIO_FORMATS):
        return get_audio_metadata(path)
    if any(path.endswith(f) for f in IMAGE_FORMATS):
        return get_image_metadata(path)
    else:
        opr.print_from("FileWhisperer - Get Metadata Omni" , f"METADATA NOT AVAILABLE FOR: {os.path.basename(path)}")


def get_all_metadata(files: list[CleanFile | dict[str, list]]) -> list[CleanFile, dict[str, list]] | None:
    
    serialized_files = []

    for f in files:
        if isinstance(f, CleanFile):            
            opr.print_from("FileWhisperer - Get all metadata", f"Collecting metadata for {os.path.basename(f)}")
            _ = get_metadata_omni(f)
            if _ is not None:
                serialized_files.append(_)
        elif isinstance(f, list):
            opr.print_from("FileWhisperer - Get all metadata", f"Collecting metadata for directory {os.path.basename(f)}")
            _ = get_all_metadata(f)
            if _ is not None:
                serialized_files.append(_)
        else: 
            opr.print_from("FileWhisperer - Get all metadata", f"Appending {f}. This shouldn't happen")
            serialized_files.append(f)

    return serialized_files

def clean_path(path: str) -> str:
    if path.startswith("& "):
        path = path[2:]

    if (path.startswith("'") and path.endswith("'")) or (path.startswith('"') and path.endswith('"')):
        path = path[1:-1]

    if "''" in path:
        path = path.replace("''", "'")

    return os.path.normpath(path)

