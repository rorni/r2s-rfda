import pytest
from itertools import accumulate

from mckit.fispact.irradiation_profile import TimeSeries, IrradiationProfile, \
    irradiation_SA2


class TestTimeSeries:
    @pytest.mark.parametrize('time, value, unit', [
        (0.5, 0.5, 'SECS'),
        (12, 12, 'SECS'),
        (59, 59, 'SECS'),
        (75, 1.25, 'MINS'),
        (120, 2.0, 'MINS'),
        (3540, 59, 'MINS'),
        (3600, 1.0, 'HOURS'),
        (7200, 2.0, 'HOURS'),
        (23*3600, 23.0, 'HOURS'),
        (24*3600, 1.0, 'DAYS'),
        (36*3600, 1.5, 'DAYS'),
        (363*24*3600, 363.0, 'DAYS'),
        (365*24*3600, 1.0, 'YEARS'),
        (2*365*24*3600, 2.0, 'YEARS')
    ])
    def test_adjust_time(self, time, value, unit):
        adj_val, adj_unit = TimeSeries.adjust_time(time)
        assert adj_unit == unit
        assert adj_val == value


class TestIrradiationProfile:
    @pytest.fixture
    def irr_prof(self):
        irr = IrradiationProfile(norm_flux=2.0)
        irr.irradiate(5.0, 12, units='MINS')
        irr.relax(20, units='MINS', record='ATOMS')
        irr.irradiate(1.0, 2, units='HOURS', record='SPEC')
        irr.relax(1, units='HOURS', record='SPEC')
        irr.relax(2, units='MINS', record='ATOMS')
        return irr

    def test_zero_index(self, irr_prof):
        assert irr_prof.zero_index() == 2

    @pytest.mark.parametrize('flux, duration, units, record, exception', [
        (5.0, 10, 'HOURS', 'ABCD', ValueError),
        (5.0, 10, 'ABCD', None, KeyError),
        (-5.0, 10, 'MINS', None, ValueError),
        (5.0, -10, 'MINS', None, ValueError)
    ])
    def test_irradiate_failure(self, irr_prof, flux, duration, units, record, exception):
        with pytest.raises(exception):
            irr_prof.irradiate(flux, duration, units, record)

    @pytest.mark.parametrize('times', [
        list(accumulate([720, 1200, 7200, 3600, 120]))
    ])
    def test_measure_times(self, irr_prof, times):
        measures = irr_prof.measure_times()
        assert measures == times

    @pytest.mark.parametrize('duration, units, record, exception', [
        (10, 'HOURS', 'ABCD', ValueError),
        (10, 'ABCD', None, KeyError),
        (-10, 'MINS', None, ValueError)
    ])
    def test_relax(self, irr_prof, duration, units, record, exception):
        with pytest.raises(exception):
            irr_prof.relax(duration, units, record)

    @pytest.mark.parametrize('input, times, flux, record', [
        (['SPEC', 20, 'MINS'], [720, 480, 720, 7200, 3600, 120], [5.0, 0, 0, 1.0, 0, 0], ['', 'SPEC', 'ATOMS', 'SPEC', 'SPEC', 'ATOMS']),
        (['ATOMS', 3, 'HOURS'], [720, 1200, 7200, 1680, 1920, 120], [5.0, 0, 1.0, 0, 0, 0], ['', 'ATOMS', 'SPEC', 'ATOMS', 'SPEC', 'ATOMS']),
        (['SPEC', 12730, 'SECS'], [720, 1200, 7200, 3600, 10, 110], [5.0, 0, 1.0, 0, 0, 0], ['', 'ATOMS', 'SPEC', 'SPEC', 'SPEC', 'ATOMS']),
        (['SPEC', 7, 'MINS'], [420, 300, 1200, 7200, 3600, 120], [5.0, 5.0, 0, 1.0, 0, 0], ['SPEC', '', 'ATOMS', 'SPEC', 'SPEC', 'ATOMS']),
        (['ATOMS', 1, 'HOURS'], [720, 1200, 1680, 5520, 3600, 120], [5.0, 0, 1.0, 1.0, 0, 0], ['', 'ATOMS', 'ATOMS', 'SPEC', 'SPEC', 'ATOMS'])
    ])
    def test_insert_record(self, irr_prof, input, times, flux, record):
        irr_prof.insert_record(*input)
        assert list(irr_prof._times.durations()) == times
        assert irr_prof._flux == flux
        assert irr_prof._record == record

    @pytest.mark.parametrize('nominal, output', [
        (10, [
            'FLUX 25.0',
            'TIME 12.0 MINS ',
            'FLUX 0.0',
            'TIME 20.0 MINS ATOMS',
            'FLUX 5.0',
            'TIME 2.0 HOURS SPEC',
            'FLUX 0',
            'ZERO',
            'TIME 1.0 HOURS SPEC',
            'TIME 2.0 MINS ATOMS'
        ])
    ])
    def test_output(self, irr_prof, nominal, output):
        lines = irr_prof.output(nominal_flux=nominal)
        assert lines == output


@pytest.fixture
def irr_profile():
    irr = IrradiationProfile(norm_flux=1)
    irr.irradiate(0.05, 1, units='YEARS', record='ATOMS')
    irr.irradiate(1.0, 10, units='MINS', record='ATOMS')
    return irr


@pytest.fixture
def rel_profile():
    rel = IrradiationProfile()
    rel.relax(1, units='HOURS', record='ATOMS')
    rel.relax(23, units='HOURS', record='ATOMS')
    rel.relax(9, units='DAYS', record='ATOMS')
    rel.relax(355, units='DAYS', record='ATOMS')
    return rel
