# -*- coding: utf-8 -*-

import argparse
import pickle
import configparser
from pathlib import Path

from . import prepare, run, fetch, source, utils


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
    subparsers = parser.add_subparsers(dest='action', required=True)

    parser_common = argparse.ArgumentParser(add_help=False)
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
        'time', type=utils.convert_time_literal, 
        help='time moment, for which gamma source must be generated.'
    )
    parser_source.add_argument(
        '-d', '--distribution', type=int, nargs='?', default=1, 
        help='the first number of source distributions to be generated.'
    )
    parser_source.add_argument(
        '-z', '--zero', action='store_true', 
        help='set end of irradiation as time zero.'
    )

    args = parser.parse_args()
    return dict(vars(args))


def main():
    command = arg_parser()
    path = Path(command['folder'])
    if command['action'] == 'prepare':
        # create folder
        path.mkdir()
        casepath = Path(path / 'cases')
        casepath.mkdir()
        
        model, datalib, fispact = load_task(command['config'])
        # try:
        config = prepare.create_tasks(
            casepath, 
            mcnp_name=model['mcnp'], 
            fmesh_name=model['fmesh'],
            tally_name=int(model['tally']),
            min_volume=float(model['minvol']),
            libs=datalib,
            libxs=fispact['libxs'],
            inventory=fispact['inventory'],
            approach=model['approach'],
            norm_flux=float(fispact['norm_flux'])
        )
        # except:
        #    pass
        save_config(path, **config)
        
    else:
        config = load_config(path)
        if command['action'] == 'run':
            threads = command['threads']
            task_list = config['task_list']
            run.run_tasks(task_list, threads=threads)

        elif command['action'] == 'fetch':
            fetch.collect(path, config)
            
        elif command['action'] == 'source':
            filename = path / 'gamma.dat'
            with open(filename, 'br') as f:
                gamma_data = pickle.load(f)
            sd = command['distribution']
            time_m = utils.convert_time_literal(command['time'])
            print(gamma_data.axes, gamma_data.labels)
            if command['zero']:
                pass
            sdef = source.create_source(gamma_data, time_m, start_distr=sd)
            with open(path / 'sdef.i', 'w') as f:
                f.write(sdef)
