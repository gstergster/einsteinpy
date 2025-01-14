import numpy as np
import sympy

from einsteinpy.symbolic.constants import Cosmo_Const, G, c
from einsteinpy.symbolic.einstein import EinsteinTensor
from einsteinpy.symbolic.helpers import _change_name
from einsteinpy.symbolic.tensor import BaseRelativityTensor, _change_config


class StressEnergyMomentumTensor(BaseRelativityTensor):
    """
    Class for defining Stress-Energy Coefficient Tensor
    """

    def __init__(
        self,
        arr,
        syms,
        config="ll",
        parent_metric=None,
        parent_spacetime=None,
        name="StressEnergyMomentumTensor",
    ):
        """
        Constructor and Initializer

        Parameters
        ----------
        arr : ~sympy.tensor.array.dense_ndim_array.ImmutableDenseNDimArray or list
            Sympy Array or multi-dimensional list containing Sympy Expressions
        syms : tuple or list
            Tuple of crucial symbols denoting time-axis, 1st, 2nd, and 3rd axis (t,x1,x2,x3)
        config : str
            Configuration of contravariant and covariant indices in tensor. 'u' for upper and 'l' for lower indices. Defaults to 'll'.
        parent_metric : ~einsteinpy.symbolic.metric.MetricTensor or None
            Corresponding Metric for the Stress-Energy Coefficient Tensor.
            Defaults to None.
        parent_spacetime : ~einsteinpy.symbolic.spacetime.GenericSpacetime or None
            Spacetime object associated with this Tensor.
        name : str
            Name of the Tensor. Defaults to "StressEnergyMomentumTensor".

        Raises
        ------
        TypeError
            Raised when arr is not a list or sympy Array
        TypeError
            syms is not a list or tuple
        ValueError
            config has more or less than 2 indices

        """
        super(StressEnergyMomentumTensor, self).__init__(
            arr=arr,
            syms=syms,
            config=config,
            parent_metric=parent_metric,
            parent_spacetime=parent_spacetime,
            name=name,
        )
        self._order = 2
        if not len(config) == self._order:
            raise ValueError("config should be of length {}".format(self._order))

    @classmethod
    def from_metric(cls, metric):
        t_einstein = EinsteinTensor.from_metric(metric)
        stress_tensor = (
            c**4
            / (8 * sympy.pi * G)
            * (t_einstein.tensor() - Cosmo_Const * metric.lower_config().tensor())
        )
        return cls(stress_tensor, metric.syms, config="ll", parent_metric=metric)

    @classmethod
    def from_einstein(cls, einstein):
        metric = einstein.parent_metric
        stress_tensor = einstein.change_config("ll").tensor()
        # (
        #    c**4
        #    / (8 * sympy.pi * G)
        #    * (einstein.tensor() - Cosmo_Const * metric.lower_config().tensor())
        # )
        return cls(stress_tensor, metric.syms, config="ll", parent_metric=metric)

    def lorentz_transform(self, transformation_matrix):
        """
        Performs a Lorentz transform on the tensor.

        Parameters
        ----------
            transformation_matrix : ~sympy.tensor.array.dense_ndim_array.ImmutableDenseNDimArray or list
                Sympy Array or multi-dimensional list containing Sympy Expressions

        Returns
        -------
            ~einsteinpy.symbolic.stress_energy_momentum.StressEnergyMomentumTensor
                lorentz transformed tensor

        """
        t = super(StressEnergyMomentumTensor, self).lorentz_transform(
            transformation_matrix
        )
        return StressEnergyMomentumTensor(
            t.tensor(),
            syms=self.syms,
            config=self._config,
            parent_metric=None,
            name=_change_name(self.name, context="__lt"),
        )
