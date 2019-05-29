import pickle


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

