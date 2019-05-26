import pickle
from pathlib import Path

from .constants import TIME_UNITS


__all__ = ['adjust_time']


def save_config(cwd, **conf_params):
    """Saves activation task configuration.

    Parameters
    ----------
    cwd : Path
        Activation task working directory.
    **conf_params : dict
        An array of keyword-value pairs to be saved.
    """
    filename = cwd / 'settings.cfg'
    with open(filename, 'bw') as f:
        pickle.dump(conf_params, f, pickle.HIGHEST_PROTOCOL)


def load_config(cwd):
    """Loads activation task configuration.

    Parameters
    ----------
    cwd : Path
        Activation task working directory.

    Returns
    -------
    conf_params : dict
        A dictionary of key-value pairs.
    """
    filename = cwd / 'settings.cfg'
    with open(filename, 'br') as f:
        conf_params = pickle.load(f)
    return conf_params


def fetch_folder(folder, read_only=False):
    """Fetches the specified folder.

    If the specified folder does not exist then it will be
    created. If the file with a such name already exist, then
    exception will be raised. read_only flag can be used to
    not overwrite already existing folder.

    Parameters
    ----------
    folder : str
        Folder name.
    read_only : bool
        Flag if the folder is readonly - not to overwrite the results.

    Returns
    -------
    path : Path
        Path object of the folder.
    """
    path = Path(folder)
    if path.exists() and not path.is_dir():
        raise FileExistsError("Such file exists but it is not a folder.")
    elif not path.exists():
        if read_only:
            raise FileNotFoundError("Data directory not found")
        else:
            path.mkdir()
    return path


_sort_units = ('YEARS', 'DAYS', 'HOURS', 'MINS', 'SECS')


def adjust_time(time):
        for unit in _sort_units:
            d = time / TIME_UNITS[unit]
            if d >= 1:
                return d, unit
        return time, 'SECS'
