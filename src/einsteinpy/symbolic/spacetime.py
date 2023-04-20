import numpy as np
import sympy
from sympy.functions.special.tensor_functions import LeviCivita
#from sympy import simplify, tensorcontraction, tensorproduct

from .helpers import _change_name
from .tensor import BaseRelativityTensor, _change_config, tensor_product
from .vector import GenericVector
from .metric import MetricTensor
from .levicivita import LeviCivitaAlternatingTensor
from .christoffel import ChristoffelSymbols
from .riemann import RiemannCurvatureTensor
from .ricci import RicciScalar, RicciTensor
from .einstein import EinsteinTensor
from .weyl import WeylTensor, BelRobinsonTensor



class GenericSpacetime:

    def __init__( self,
                    metric,
                    chris=None,
                    riemann=None,
                    ricci=None,
                    einstein=None,
                    sem_tensor=None,
                    name = "GenericSpacetime"):

        self._metric = metric
        self._chris = chris
        self._riemann = riemann
        self._ricci = ricci
        self._ricci_s = None
        self._einstein = einstein
        self._sem_tensor = sem_tensor
        self._levi_civita = None
        self._weyl = None
        self._belrob = None

    @property
    def EinsteinTensor(self):
        if self._einstein is None:
            self._einstein = EinsteinTensor.from_ricci(self.RicciTensor, self.RicciScalar)
        return self._einstein

    @EinsteinTensor.setter
    def EinsteinTensor(self, value):
        self._einstein = value

    @property
    def RicciScalar(self):
        if self._ricci_s is None:
            self._ricci_s = RicciScalar.from_riccitensor(self.RicciTensor)
        return self._ricci_s

    @RicciScalar.setter
    def RicciScalar(self, value):
        self._ricci_s = value

    @property
    def RicciTensor(self):
        if self._ricci is None:
            self._ricci = RicciTensor.from_riemann(self.RiemannTensor)
        return self._ricci

    @RicciTensor.setter
    def RicciTensor(self, value):
        self._ricci = value

    @property
    def RiemannTensor(self):
        if self._riemann is None:
            self._riemann = RiemannCurvatureTensor.from_christoffels(self.ChristoffelSymbols)
        return self._riemann

    @RiemannTensor.setter
    def RiemannTensor(self, value):
        self._riemann = value

    @property
    def WeylTensor(self):
        if self._weyl is None:
            self._weyl = WeylTensor.from_tensors(self.Metric, self.RiemannTensor, self.RicciTensor, self.RicciScalar)
            self._weyl._parent_spacetime = self
        return self._weyl

    @WeylTensor.setter
    def WeylTensor(self, value):
        self._weyl = value
    
    @property
    def BelRobinsonTensor(self):
        if self._belrob is None:
            self._belrob = BelRobinsonTensor.from_weyl(self.WeylTensor)
        return self._belrob

    @BelRobinsonTensor.setter
    def BelRobinsonTensor(self, value):
        self._belrob = value

    @property
    def ChristoffelSymbols(self):
        if self._chris is None:
            self._chris = ChristoffelSymbols.from_metric(self.Metric)
        return self._chris

    @ChristoffelSymbols.setter
    def ChristoffelSymbols(self, value):
        self._chris = value

    @property
    def LeviCivitaTensor(self):
        if self._levi_civita is None:
            self._levi_civita = LeviCivitaAlternatingTensor.from_metric(self.Metric)
        return self._levi_civita

    @LeviCivitaTensor.setter
    def LeviCivitaTensor(self, value):
        self._levi_civita = value

    @property
    def SEMTensor(self):
        if self._sem_tensor is None:
            self._sem_tensor = StressEnergyMomentumTensor.from_einstein(self.EinsteinTensor)
        return self._sem_tensor

    @SEMTensor.setter
    def SEMTensor(self, value):
        self._sem_tensor = value

    @property
    def Metric(self):
        return self._metric


    def EinsteinEquations(self):
        return sympy.Eq(self.EinsteinTensor, 8*sympi.pi * self.SEMTensor)


    def GeodesicEquation(self, wline, apar):
        chris = self.ChristoffelSymbols.change_config("ull")
        wline = wline.change_config("u")
        dx_ds = GenericVector(wline.tensor().diff(apar), syms=wline.syms, config="u")
        rhs = tensor_product(tensor_product(chris, dx_ds, 1, 0), dx_ds, 1, 0)
        d2x_ds2 = dx_ds.tensor().diff(apar)
        return sympy.Eq(d2x_ds2, - rhs.tensor())


    def covariant_derivative(self, T):
        """


        """
        chris = self.ChristoffelSymbols
        if not chris.config == "ull":
            chris = chris.change_config(newconfig="ull", metric=self._metric)

        syms = chris.symbols()

        Td = []
        try:
            for s in syms:
                Td.append(T.tensor().diff(s))
            Td = BaseRelativityTensor(Td, syms=syms, config="l" + T.config, parent_metric=self.Metric)

            for i in range(T.order):
                if T.config[i] == "u":
                    Td.arr += tensor_product(chris, T, 1, i).arr
                if T.config[i] == "l":
                    Td.arr -= tensor_product(chris, T, 0, i).arr
        except AttributeError:
            for s in syms:
                Td.append(T.diff(s))
            Td = BaseRelativityTensor(Td, syms=syms, config="l", parent_metric=self.Metric)

        return Td

