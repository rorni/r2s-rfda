# -*- coding: utf-8 -*-

import argparse
import pickle
import configparser
from pathlib import Path

from . import prepare, run, fetch, source


def load_task(filename):
    """Loads task configuration.
    
    Parameters
    ----------
    filename : str
        Name of task configuration file.

    Returns
    -------
    model_conf : dict
        Model configuraion values.
    data_conf : dict
        Data library configuration.
    fispact_conf : dict
        Fispact configuration values.
    """
    conf_par = configparser.ConfigParser()
    with open(filename) as f:
        conf_par.read_file(f)
    model_conf = dict(conf_par['MODEL'])
    data_conf = dict(conf_par['DATALIB'])
    fispact_conf = dict(conf_par['FISPACT'])
    return model_conf, data_conf, fispact_conf


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


def arg_parser():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(prog='R2S method')
    subparsers = parser.add_subparsers(dest='action')

    parser_common = argparse.ArgumentParser()
    parser_common.add_argument(
        'folder', type=str, help='Working folder'
    )

    parser_prepare = subparsers.add_parser('prepare', parents=[parser_common])
    parser_run = subparsers.add_parser('run', parents=[parser_common])
    parser_fetch = subparsers.add_parser('fetch', parents=[parser_common])
    parser_source = subparsers.add_parser('source', parents=[parser_common])

    # prepare arguments
    parser_prepare.add_argument(
        'config', type=str, help='Configuration file.'
    )    

    # run arguments
    parser_run.add_argument(
        '-t', '--threads', nargs='?', type=int, default=1, 
        help='the number of worker processes to be run'
    )

    # fetch arguments

    # source arguments
    parser_source.add_argument(
        'source', type=str, help='file for generated SDEF'
    )
    parser_source.add_argument(
        '-d', '--distribution', type=int, nargs='?', default=1, 
        help='the first number of source distributions to be generated.'
    )

    args = parser.parse_args()
    return dict(vars(args))


def main():
    command = arg_parser()
    if command['action'] == 'prepare':
        model, datalib, fispact = load_task(command['config'])
        # read model
        # read fmesh
        # read template

        # calculate volumes
        # select materials & densities
        # calculate masses
        # create folder

        if fispact['approach'] == 'full':
            # prepare full mesh cases (fluxes, masses, template)
            pass
        elif fispact['approach'] == 'simple':
            # prepare simple mesh cases (F0, M0, ebins, materials, template)
            # prepare adjustment coefficients.
            pass
        else:
            # unknown approach
            pass
        # save config
        
    elif command['action'] == 'run':
        path = Path(command['folder'])
        threads = command['threads']
        run.run_tasks(path, threads=threads)

    elif command['action'] == 'fetch':
        pass
    elif command['action'] == 'source':
        pass
