# -*- coding: utf-8 -*-


def create_source(gamma_data, start_distr=1):
    """Creates MCNP SDEF for gamma source.

    Parameters
    ----------
    gamma_data : SparseData
        Data on gamma yield for every cell and voxel.
    start_distr : int
        Starting SDEF distribution number.
    
    Returns
    -------
    sdef : str
        MCNP SDEF description.
    """
    raise NotImplementedError
