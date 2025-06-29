# File Utilities
# Created 6/26/2025

from datetime import datetime

def get_timestamped_filename(save_path: str, prefix: str, ext: str) -> str:
    '''
    Returns a unique formatted filename for each second.\n
    Include a period in file extensions, and do not include a trailing slash
    in save paths! \n filename follows the format:
    "{save_path}/{prefix}_YearMonthDay_HourMinuteSecond{ext}"
    '''
    if (ext.find('.') == -1):
        raise ValueError("File extension arguments must include a leading period.")
    if (save_path[-1] == '/'):
        raise ValueError("Save path must not include a trailing slash.")
    if (prefix.find('.') != -1 or prefix.find('/') != -1):
        raise ValueError("Filename prefix must not include periods or slashes.")

    timestamp = datetime.now().strftime("%2Y%m%d_%H%M%S")
    filename = f"{save_path}/{prefix}_{timestamp}{ext}"
    return filename


def write_file_header(filename: str, pts: int = None, header: str = None):
    '''
    Will write a standard .pcd header if header argument is not specified:\n
    header = [
        "VERSION .7", "FIELDS x y z rgb",
        "SIZE 4 4 4 4", "TYPE F F F F",
        "COUNT 1 1 1 1", "WIDTH pts",
        "HEIGHT 1", "VIEWPOINT 0 0 0 1 0 0 0",
        "POINTS pts", "DATA ascii"
    ]
    '''
    if (filename.find('.pcd') != -1 and pts is None):
        raise ValueError("You must specify the number of points in the cloud.")

    if filename.find('.pcd') != -1 and header is None:
        header = ["VERSION .7\n",
                    "FIELDS x y z rgb\n",
                    "SIZE 4 4 4 4\n",
                    "TYPE F F F F\n",
                    "COUNT 1 1 1 1\n",
                    f"WIDTH {pts}\n",
                    "HEIGHT 1\n",
                    "VIEWPOINT 0 0 0 1 0 0 0\n",
                    f"POINTS {pts}\n",
                    "DATA ascii\n"
                    ]
    
    with open(filename, "a") as file:
        file.writelines(header)