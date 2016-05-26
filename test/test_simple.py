
import datetime
import numpy as np
from cinfdata import Cinfdata

DATA_CHECKSUM = 12525.0000008
METADATA = {
    'comment': '', 'tof_liner_voltage': None, 'tof_iterations': None,
    'timestep': 0.1, 'id': 5417L, 'preamp_range': -7, 'tof_pulse_width': None,
    'pre_wait_time': None, 'tof_ion_energy': None, 'tof_R2_voltage': None,
    'mass_label': None, 'tof_R1_voltage': None, 'sem_voltage': 1798.83,
    u'unixtime': 1464261944L, 'type': 4L, 'pass_energy': None,
    'time': datetime.datetime(2016, 5, 26, 13, 25, 44),
    'sample_temperature': None, 'tof_focus_voltage': None,
    'tof_pulse_voltage': None, 'tof_emission_current': None,
    'tof_deflection_voltage': None, 'tof_p1_2': None, 'tof_p1_0': None,
    'tof_p1_1': None, 'tof_lens_E': None, 'tof_lens_D': None,
    'tof_lens_A': None, 'tof_lens_C': None, 'tof_lens_B': None
}

cinfdata = Cinfdata('tof', use_caching=True)
# Get from database
assert np.isclose(cinfdata.get_data(5417).sum(), DATA_CHECKSUM)
assert cinfdata.get_metadata(5417) == METADATA
print('Test database OK')
# And now fetch from cache
assert np.isclose(cinfdata.get_data(5417).sum(), DATA_CHECKSUM)
assert cinfdata.get_metadata(5417) == METADATA
print('Test cache OK')

