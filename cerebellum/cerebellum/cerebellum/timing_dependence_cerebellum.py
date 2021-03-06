from data_specification.enums.data_type import DataType

from spynnaker.pyNN.models.neuron.plasticity.stdp.timing_dependence\
    .abstract_timing_dependence import AbstractTimingDependence
from spynnaker.pyNN.models.neuron.plasticity.stdp.synapse_structure\
    .synapse_structure_weight_only import SynapseStructureWeightOnly
from spynnaker.pyNN.models.neuron.plasticity.stdp.common \
    import plasticity_helpers

import logging
import math

logger = logging.getLogger(__name__)

# Constants
LOOKUP_SIN_SIZE = 512
LOOKUP_SIN_SHIFT = 0


class TimingDependenceCerebellum(AbstractTimingDependence):

    def __init__(self, tau=40.0, peak_time=100.0):
        AbstractTimingDependence.__init__(self)

        self.tau = tau
        self.peak_time = peak_time

        self._synapse_structure = SynapseStructureWeightOnly()

    def is_same_as(self, other):
        if (other is None) or (not isinstance(
                other, TimingDependenceCerebellum)):
            return False
        return ((self.tau == other.tau) and (self.peak_time == other.peak_time))

    @property
    def vertex_executable_suffix(self):
        return "cerebellum"

    @property
    def pre_trace_n_bytes(self):

        # Trace entries consist of a single 16-bit number
        return 0

    def get_parameters_sdram_usage_in_bytes(self):
        return 4 + (2 * LOOKUP_SIN_SIZE)

    @property
    def n_weight_terms(self):
        return 1

    def write_parameters(self, spec, machine_time_step, weight_scales):
        # Write peak time in timesteps
        peak_time_data = int(self.peak_time * (1000.0 / machine_time_step) - LOOKUP_SIN_SIZE/2  + 0.5)
        print "peak time data:", peak_time_data, "peak_time:", self.peak_time
        spec.write_value(data=peak_time_data,
                         data_type=DataType.INT32)

        # Calculate time constant reciprocal
        time_constant_reciprocal = (1.0 / float(self.tau)) * (machine_time_step / 1000.0)
        
        # This offset is the quasi-symmetry point
        sinadd_pwr = 20
        zero_offset = math.atan(-1./sinadd_pwr)
        max_value = math.exp(-zero_offset)*math.cos(zero_offset)**sinadd_pwr
        
        # Generate LUT
        last_value = None
        for i in range(-LOOKUP_SIN_SIZE/2,-LOOKUP_SIN_SIZE/2 + LOOKUP_SIN_SIZE):
            # Apply shift to get time from index
            time = (i << LOOKUP_SIN_SHIFT)
            
            # Multiply by time constant and calculate negative exponential
            value = float(time) * time_constant_reciprocal + zero_offset
            # we want a single bump only, so we clip the arg at pi/2
            if abs(value) > math.pi/2.:
                exp_float = 0.0
            else:
                exp_float = math.exp(-value) * math.cos(value)**sinadd_pwr / max_value
            print i, exp_float

            # Convert to fixed-point and write to spec
            last_value = plasticity_helpers.float_to_fixed(exp_float, plasticity_helpers.STDP_FIXED_POINT_ONE)
            spec.write_value(data=last_value, data_type=DataType.INT16)

        self._tau_last_entry = float(last_value) / float(plasticity_helpers.STDP_FIXED_POINT_ONE)

    @property
    def synaptic_structure(self):
        return self._synapse_structure

    def get_provenance_data(self, pre_population_label, post_population_label):
        prov_data = list()
        prov_data.append(plasticity_helpers.get_lut_provenance(
            pre_population_label, post_population_label, "TimingDependenceCerebellum",
            "tau_last_entry", "tau", self._tau_last_entry))
        return prov_data
