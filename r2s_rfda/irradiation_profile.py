# -*- coding: utf-8 -*-
import numpy as np

from .constants import TIME_UNITS


class TimeSeries:
    """Represents an array of time points.

    Methods
    -------
    append_interval(delta, units)
        Appends a time moment after delta passed since last time point.
    insert_point(time, units)
        Inserts a time point.
    durations()
        Gets an iterator over time intervals between time points.
    adjust_time(time)
        Gets time in best suited time units.
    """
    _sort_units = ('YEARS', 'DAYS', 'HOURS', 'MINS', 'SECS')

    def __init__(self):
        self._points = []

    def __iter__(self):
        return iter(self._points)

    def __len__(self):
        return len(self._points)

    def append_interval(self, delta, units='SECS'):
        """Appends a new time point after delta time from last point.

        Parameters
        ----------
        delta : float
            Time interval which must be added.
        units : str
            Time units in which delta value is measured. Default: 'SECS'.
        """
        if delta <= 0:
            raise ValueError('Duration cannot be less than zero')
        if self._points:
            last = self._points[-1]
        else:
            last = 0
        self._points.append(last + delta * TIME_UNITS[units])

    def insert_point(self, time, units='SECS'):
        """Inserts a new time point into time series.

        Parameters
        ----------
        time : float
            Time point to be inserted.
        units : str
            Units in which time value is measured. Default: 'SECS'.

        Returns
        -------
        index : int
            Index of position, at which new time point is inserted.
        """
        time = time * TIME_UNITS[units]
        index = np.searchsorted(self._points, time)
        self._points.insert(index, time)
        return index

    def durations(self):
        """Gets an iterator over time intervals.

        Returns
        -------
        duration : float
            Duration of time interval.
        """
        if self._points:
            yield self._points[0]
        for i in range(1, len(self._points)):
            dur = self._points[i] - self._points[i-1]
            yield dur

    @classmethod
    def adjust_time(cls, time):
        for unit in cls._sort_units:
            d = time / TIME_UNITS[unit]
            if d >= 1:
                return d, unit
        return time, 'SECS'


class IrradiationProfile:
    """Describes irradiation and relaxation.

    Parameters
    ----------
    norm_flux : float
        Flux value for normalization.
    """
    def __init__(self, norm_flux=None):
        self._norm = norm_flux
        self._flux = []
        self._times = TimeSeries()
        self._record = []
        self._zero_index = 0

    def zero_index(self):
        """Gets index of time moment, when irradiation was finished."""
        return self._zero_index

    def irradiate(self, flux, duration, units='SECS', record=None, nominal=False):
        """Adds irradiation step.

        Parameters
        ----------
        flux : float
            Flux value in neutrons per sq. cm per sec.
        duration : float
            Duration of irradiation step.
        units : str
            Units of duration. 'SECS' (default), 'MINS', 'HOURS', 'YEARS'.
        record : str
            Results record type: 'SPEC', 'ATOMS'. Default: None - no record.
        nominal : bool
            Indicate that this flux is nominal and will be used in normalization.
        """
        if record is None:
            record = ''
        elif record != 'ATOMS' and record != 'SPEC':
            raise ValueError('Unknown record')
        if flux < 0:
            raise ValueError('Flux cannot be less than zero')
        self._flux.append(flux)
        self._times.append_interval(duration, units=units)
        self._record.append(record)
        self._zero_index = len(self._times) - 1
        if nominal:
            self._norm = flux

    def measure_times(self):
        """Gets a list of times, when output is made.

        Returns
        -------
        times : list[float]
            Output times in seconds.
        """
        return list(self._times)

    def relax(self, duration, units='SECS', record=None):
        """Adds relaxation step.

        Parameters
        ----------
        duration : float
            Duration of irradiation step.
        units : str
            Units of duration. 'SECS' (default), 'MINS', 'HOURS', 'YEARS'.
        record : str
            Results record type: 'SPEC', 'ATOMS'. Default: None - no record.
        """
        if record is None:
            record = ''
        elif record != 'ATOMS' and record != 'SPEC':
            raise ValueError('Unknown record')
        if duration <= 0:
            raise ValueError('Duration cannot be less than zero')
        self._flux.append(0)
        self._times.append_interval(duration, units=units)
        self._record.append(record)

    def insert_record(self, record, time, units='SECS'):
        """Inserts extra observation point for specified time.

        Parameters
        ----------
        record : str
            Record type.
        time : float
            Time left from the profile start.
        units : str
            Time units.
        """
        index = self._times.insert_point(time, units=units)
        self._flux.insert(index, self._flux[index])
        self._record.insert(index, record)
        if index <= self._zero_index:
            self._zero_index += 1

    def output(self, nominal_flux=None):
        """Creates FISPACT output for the profile.

        Parameters
        ----------
        nominal_flux : float
            Nominal flux at point of interest.

        Returns
        -------
        text : str
            Output.
        """
        if self._norm is not None and nominal_flux is not None:
            norm_factor = nominal_flux / self._norm
        else:
            norm_factor = 1
        lines = []
        last_flux = 0
        for i, (flux, dur, rec) in enumerate(zip(self._flux, self._times.durations(), self._record)):
            cur_flux = flux * norm_factor
            if cur_flux != last_flux:
                lines.append('FLUX {0:.5}'.format(cur_flux))
            time, unit = self._times.adjust_time(dur)
            lines.append('TIME {0:.5} {1} {2}'.format(time, unit, rec))
            last_flux = cur_flux
            if i == self._zero_index:
                last_flux = 0
                lines.append('FLUX 0')
                lines.append('ZERO')
        # if last_flux > 0:
        #    lines.append('FLUX 0')
        return lines


def irradiation_SA2():
    """Creates SA2 irradiation profile.

    Returns
    -------
    irr_prof : IrradiationProfile
        Irradiation profile object.
    """
    irr_prof = IrradiationProfile(4.5643E+12)
    irr_prof.irradiate(2.4452E+10, 2, units='YEARS', record='ATOMS')
    irr_prof.irradiate(1.8828E+11, 10, units='YEARS', record='ATOMS')
    irr_prof.relax(0.667, units='YEARS', record='ATOMS')
    irr_prof.irradiate(3.7900E+11, 1.330, units='YEARS', record='ATOMS')
    for i in range(17):
        irr_prof.relax(3920, record='ATOMS')
        irr_prof.irradiate(4.5643E+12, 400, record='ATOMS')
    irr_prof.relax(3920, record='ATOMS')
    irr_prof.irradiate(6.3900E+12, 400, record='ATOMS')
    irr_prof.relax(3920, record='ATOMS')
    irr_prof.irradiate(6.3900E+12, 400, record='ATOMS')
    irr_prof.relax(3920, record='ATOMS')
    irr_prof.irradiate(6.3900E+12, 400, record='ATOMS')
    irr_prof.relax(1, record='ATOMS')
    irr_prof.relax(299, record='ATOMS')
    irr_prof.relax(25, units='MINS', record='ATOMS')
    irr_prof.relax(30, units='MINS', record='ATOMS')
    irr_prof.relax(2, units='HOURS', record='ATOMS')
    irr_prof.relax(2, units='HOURS', record='ATOMS')
    irr_prof.relax(5, units='HOURS', record='ATOMS')
    irr_prof.relax(14, units='HOURS', record='ATOMS')
    irr_prof.relax(2, units='DAYS', record='ATOMS')
    irr_prof.relax(4, units='DAYS', record='ATOMS')
    irr_prof.relax(23, units='DAYS', record='ATOMS')
    irr_prof.relax(60, units='DAYS', record='ATOMS')
    irr_prof.relax(275.25, units='DAYS', record='ATOMS')
    irr_prof.relax(2, units='YEARS', record='ATOMS')
    irr_prof.relax(7, units='YEARS', record='ATOMS')
    irr_prof.relax(20, units='YEARS', record='ATOMS')
    irr_prof.relax(20, units='YEARS', record='ATOMS')
    irr_prof.relax(50, units='YEARS', record='ATOMS')
    irr_prof.relax(900, units='YEARS', record='ATOMS')
    return irr_prof
