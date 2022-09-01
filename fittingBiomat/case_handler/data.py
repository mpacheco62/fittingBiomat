from threading import Thread
from scipy.interpolate import interp1d
import numpy as np

class _ThreadDataCase(Thread):
    def __init__(self, _funToRun, parameters, iter, **kwargs):
        Thread.__init__(self, daemon=True)
        self._funToRun = _funToRun
        self.parameters = parameters
        self.iter = iter
        self.kwargs = kwargs

    def run(self):
        self.residual = self._funToRun(self.parameters, self.iter, **self.kwargs)
        return


# FUN tiene que devolver una tupla x, y
class DataCase:
    def __init__(self, sim, exp=None, fun=None, weights=None):
        self.exp = list()
        self.sim = sim
        self.fun = list()
        self.weights = list()
        self._idata = 0

        if (exp is not None) and (fun is not None):
            self.exp.append(exp)
            self.fun.append(fun)
            if weights is None:
                self.weights.append(lambda x, y: 1.0)
            else:
                self.weights.append(weights)


    def add(self, exp, fun, weights=None):
        self.exp.append(exp)
        self.fun.append(fun)
        if weights is None:
            self.weights.append(lambda x, y: 1.0)
        else:
            self.weights.append(weights)

    def _toInter(self, data):
        x, y = data
        return interp1d( x, y, fill_value='extrapolate')

    def run(self, parameters, iter, **kwargs):
        result = self.sim.run(iter=iter, parameters=parameters, **kwargs)
        residual = []

        for exp, fun, weights in zip(self.exp, self.fun, self.weights):
            x = exp[:,0]
            y_exp = exp[:,1]
            # TODO agregar alternativas de como se hace la interpolacion
            y_sim = self._toInter(fun(result))(x)
            weights_arr = weights(x, y_exp)
            iresidual = weights_arr*(y_exp - y_sim)
            residual.append(iresidual)

        return np.concatenate(residual)

    def factoryThread(self, parameters, iter, **kwargs):
        return _ThreadDataCase(self.run, parameters, iter, **kwargs)

        




    

