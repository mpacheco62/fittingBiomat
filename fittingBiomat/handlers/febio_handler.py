"""
This module allows to execute flexible fitting procedures, with full control
of the fitting method, variables, calculations and experimental data formats.

# TODO

- LMFIT library works on serial numerical approximations to obtain a jacobian,
     however, when the residual function is time expensive, the fitting process
     is too long. A parallel jacobian calculation is implemented, but it is quite rudimental,
     so is disabled in the source code by now.

"""

import numpy as np
import lmfit
from scipy.interpolate import interp1d
import os
import subprocess
import threading
import sys
import time
from datetime import datetime
from sklearn.metrics import r2_score
from scipy.ndimage import interpolation

class Case:
    """Clase que crea nuevos casos para ajustar

    Examples
    --------
    TODO!!!!!!!!!!
    En el archivo filesBases (caso1.dat) se tiene el valor de HD_COEFF como
    '%HD_COEFF%'. Además supongamos que queremos reemplazarlo por 10.0, por
    lo tanto tenemos que crear un diccionario con esa llave y el valor.

    >>> parametros = {'HD_COEFF': 10.0}
    >>> caso1 = CreatorCase(['caso1.dat'],'casoTemp')
    >>> caso1.addParameter('HD_COEFF')
    >>> caso1.create(parametros)
    >>> caso1.run()

    Con lo anterior se crea un dat temporal llamado casoTemp.dat, se reemplaza
    el texto %HD_COEFF% por el valor correspondiente en el diccionario y
    finalmente se corre el caso vulcan.

    Si se quiere correr el caso nuevamente pero solo cambiando el valor del
    parametro HD_COEFF, se puede reutilizar lo anterior.

    >>> parametros['HD_COEFF'] = 20.0
    >>> caso1.create(parametros)
    >>> caso1.run()
    TODO!!!!!!!!!!!!!!
    """
    def __init__(self, modelName, matID, subFolder, expData, simFcn, retainLog=False, retainBinary=False):

        self.modelName = modelName
        self.modelBinary = modelName.split('.feb')[0]+'.xplt'
        self.matID = matID
        self.subFolder = subFolder
        self.expData = expData
        self.current_directory = os.getcwd()
        self.simFcn = simFcn
        self.parameters = []
        self.retainLog = retainLog
        self.retainBinary = retainBinary

    def addParameter(self,param):
        self.parameters.append(param)


    # TODO privado
    def writeCase(self,params,iter):
        pars = dict(params.valuesdict())
        originalTree = ET.parse(self.modelName)
        tree = originalTree
        root = tree.getroot()
        for material in root.findall('.//material'):
            if(material.attrib['id'] == str(self.matID) or material.attrib['name'] == str(self.matID)):
                for const in material:
                    #print(const.tag, self.parameters)
                    if(const.tag in self.parameters):
                        #print(pars[const.tag])
                        const.text = '{:.20e}'.format(pars[const.tag])
                        #print(const.tag,const.text)
        #print(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder))
        tree.write(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder)+'/'+self.modelName,encoding='ISO-8859-1', xml_declaration=True)

        # for p in pars.keys():
        #     if params[p].expr == None:
        #         tree = originalTree
        #         root = tree.getroot()
        #         for material in root.findall('.//material'):
        #             if(material.attrib['id'] == str(self.matID)):
        #                 for const in material:
        #                     #print(const.tag, self.parameters)
        #                     if(const.tag in self.parameters and const.tag == p):
        #                         #print(pars[const.tag])
        #                         const.text = '{:.20e}'.format(pars[const.tag]*(1+0.05)/1000.0)
        #                     if(const.tag in self.parameters and const.tag != p):
        #                         const.text = '{:.20e}'.format(pars[const.tag]/1000.0)
        #                         #print(const.tag,const.text)
        #         #print(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder))
        #         tree.write(os.path.join(self.current_directory, 'iter'+str(iter),self.subFolder,p)+'/'+self.modelName.split('.')[0]+'_'+p+".feb",encoding='ISO-8859-1', xml_declaration=True)

    # TODO privado
    def verifyFolders(self, iter):
        iterDir = os.path.join(self.current_directory, 'iter'+str(iter))
        if not os.path.exists(iterDir):
            os.makedirs(iterDir)
        simDir = os.path.join(iterDir, self.subFolder)
        if not os.path.exists(simDir):
            os.makedirs(simDir)
        # for par in pars.keys():
        #     if p[par].expr == None:
        #         paramPath = os.path.join(simDir, par)
        #         if not os.path.exists(paramPath):
        #             os.makedirs(paramPath)

    def result(self, iter):
        file = 'iter'+str(iter)+'/'+self.subFolder+'/'+self.modelBinary
        xplt = interFEBio.xplt(file)
        return xplt

    def run(self, iter, params):

        self.verifyFolders(self, iter)
        self.writeCase(self, params, iter):

        if(self.retainLogs):
            command = "febio3"+" -i "+self.casos[caso].modelName
        else:
            command = "febio3"+" -i "+self.casos[caso].modelName+" -o /dev/null"

        p = subprocess.Popen([command],shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,cwd=os.path.join('iter'+str(iter),self.casos[caso].subFolder)+'/')
        print("Running simulation "+os.path.join('iter'+str(iter),self.casos[caso].subFolder)+'/'+self.casos[caso].modelName+ ". PID: ",p.pid)
        self.pid[caso] = p.pid
        p.communicate()
        p.wait()
        return self.result()

    # TODO make private
    def makeCleans(self, iter):
        #if(self.retainBinary):
        #    command = "febio3"+" -i "+self.casos[caso].modelName
        pass

