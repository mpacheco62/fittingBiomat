"""
This module allows to execute flexible fitting procedures, with full control
of the fitting method, variables, calculations and experimental data formats.

# TODO

- LMFIT library works on serial numerical approximations to obtain a jacobian,
     however, when the residual function is time expensive, the fitting process
     is too long. A parallel jacobian calculation is implemented, but it is quite rudimental,
     so is disabled in the source code by now.

"""

import lmfit
from datetime import datetime
import numpy as np

class Fit:
    '''
    Class that handles the numerical fitting algotirm.
    This class is based on lmfit library.

    '''
    def __init__(self):
        self.iter = 1
        self.p = lmfit.Parameters()
        self.mi = 0 #Used for saving fit results
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = datetime.today().strftime('%d-%m-%Y')
        self.logfileName = 'log_'+current_date+'_'+current_time+'.txt'

        self.cases = list()

    def addCase(self, case):
        '''
        Add a simulation to the fitting algorithm, including all the experimental data
        and how to obtain numerical results for this xplt file.

        Args:
        ----------

            simFcn (fuinction): Function that handles the result calculation of the simulation. Needs to be written in terms of the xplt class functions.

        '''
        self.cases.append(case)

    # def _statistics(self,p):
    #     parameters = dict(p.valuesdict())
    #     self.r2 = dict()
    #     for case in self.casos:
    #         actual = self.expfcn[case](self.results[case][0])
    #         predict = self.results[case][1]

    #         R_sq = r2_score(actual, predict)
    #         self.r2[case] = R_sq

    #     self.logfile = open(self.logfileName, 'a')
    #     self.logfile.write('iter '+str(self.iter)+'\t')
    #     self.logfile.write(datetime.now().strftime("%H:%M:%S")+':\n')
    #     self.logfile.write('\t'+'r2 = ')
    #     self.logfile.write(str(self.r2))
    #     self.logfile.write('\n')
    #     self.logfile.write('\t'+'Parameters = ')
    #     self.logfile.write(str(parameters))
    #     self.logfile.write('\n')
    #     self.logfile.close()



    def _totalResidual(self, p):
        parameter = dict(p.valuesdict())

        tcases = []
        residual = []
        for case in self.cases:
            tcase = case.factoryThread(parameter, self.iter)
            tcases.append(tcase)
            tcase.start()

        for tcase in tcases:
            tcase.join()

        for tcase in tcases:
            residual.append(tcase.residual)

        residual = np.concatenate(residual)
        return residual

    def _per_iteration(self, pars, iter, resid, *args, **kws):
        print(" ITER ", iter, [[i,pars.valuesdict()[i]] for i in pars.valuesdict()])
        self.iter = iter+3

    def optimize(self,**kwargs):
        '''
        Optimize.

        This function start the optimization algorithm.
        The residual is calculated from the simulation (using the external function provided for the case), and compare those results with the experimental data provided.


        kwargs:
        ----------

            kwargs for the lmfit.minimize function.
            >>> optimize(method='basinhopping')
        '''
        self.mi = lmfit.minimize(self._totalResidual,
                            self.p,
                            **dict(kwargs, iter_cb=self._per_iteration)
                            )
        # self.mi = lmfit.minimize(self._residual,
        #                     self.p,
        #                     iter_cb=self._per_iteration,
        #                     **kwargs
        #                     )
        lmfit.printfuncs.report_fit(self.mi.params, min_correl=0.5)
        print(lmfit.fit_report(self.mi))

    # def _signal_handler(self,sig, frame):
    #     print()
    #     print("***********************************")
    #     print("***********************************")
    #     print()
    #     print('You pressed Ctrl+C!')
    #     print("Killing the running simulations:")
    #     print(self.pid)
    #     print()
    #     print("***********************************")
    #     print("***********************************")

    #     for key in self.pid:
    #         try:
    #             parent = psutil.Process(self.pid[key])
    #         except:
    #             continue
    #         for child in parent.children(recursive=True):  # or parent.children() for recursive=False
    #             try:
    #                 child.kill()
    #             except:
    #                 print("Child process no longer exists.")
    #                 continue
    #         try:
    #             parent.kill()
    #         except:
    #             print("Parent process no longer exists.")
    #             continue
    #     sys.exit(0)
