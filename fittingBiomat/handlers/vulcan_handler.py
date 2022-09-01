from shutil import copyfile
import subprocess
import os
from vulcan import Vulcan
from . import stdout_redirects
from intervul.readpos import VulcanPosMesh

# TODO agregar warnings y/o errores de pasos o tiempo
class VulcanHandler(object):
    """Clase que crea nuevos casos y los lanza

    Para esto toma algun caso base fileBase y lo copia a una carpeta temporal
    folderTemp con el nombre newname, para luego poder lanzarlo cuando sea
    necesario.

    La forma en que se reemplazan los valores se puede definir con formatValues

    Examples
    --------
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
    """
    def __init__(self, filesBases, newname, folderTemp=".",
                 formatValues=None, scratchPath="~/scratch/", vulType='m'):
        """Inicializa la instancia con datos basicos para reemplazar

        Parameters
        ----------
        filesBases: [str, str, ...]
            Define los archivos que se utilizara como base, para la copia y el
            posterior reemplazo
        newname: str
            Define el nombre del nuevo archivo que se crea para el reemplazo
        folderTemp: str
            Define la carpeta donde ira el archivo newname, esta carpeta no
            debe ser en una ruta absoluta muy larga para no tener problemas
            con vulcan
        formatValues: None, str, dict
            Define el formato de cada parametro a reemplazar en el archivo
            - Si es None, utilza el formato estandar de Python
            - Si es str, internamente hace formatValues.format(valor)
            - Si es dict, internamente hace
              formatValues[parametro].format(valor)
        scratch_path: str
            Define donde se correran los casos, se puede definir una carpeta
            scratch distinta
        """
        scratchPath = os.path.expanduser(scratchPath)
        folderTemp = os.path.expanduser(folderTemp)
        stdout_redirects.enable_proxy()
        self.filesBases = filesBases
        self.newname = newname
        self.folderTemp = folderTemp
        self.formatValues = formatValues
        self.scratchPath = scratchPath
        self.dataToReeplace = set()
        self.vulType = vulType
        self.pan = None
        self._runned = False

    def _formatingNumbers(self, parameter, value):
        """ Metodo interno para dar formato a los valores

        Parameters
        ----------
        parameter: str
            Es el nombre del parametro a reemplazar
        value: float
            Es el valor a reemplazar
        """
        toReturn = None
        formatVal = self.formatValues
        if formatVal is None:
            toReturn = str(value)

        elif isinstance(formatVal, str):
            toReturn = formatVal.format(value)

        elif isinstance(formatVal, dict):
            if parameter in formatVal:
                toReturn = formatVal[parameter].format(value)
            else:
                toReturn = str(value)

        else:
            raise TypeError("El formato debe ser 'None', un string o un "
                            "diccionario con el formato de cada parametro")

        return toReturn

    def _copyToNewDir(self):
        """ Metodo que copia el archivo base a la nueva ubicación

        Es un metodo que copia el archivo basa a una nueva ubicacion, el metodo
        utiliza rutas absolutas, por lo que no deberian existir problemas.
        Ademas permite que en cualquier momento se cambie la variable fileBase,
        folderTemp o newname para actualizar donde se copia el archivo
        """

        newFiles = list()
        for ifile in self.filesBases:
            basepath = os.path.abspath(ifile)
            path, ext = os.path.splitext(basepath)
            newname = self.newname + ext

            newfilePath = os.path.abspath(self.folderTemp)
            newfilePath = os.path.join(newfilePath, newname)
            os.makedirs(os.path.dirname(newfilePath), exist_ok=True)
            # print(newfilePath)
            copyfile(basepath, newfilePath)

            newFiles.append(newfilePath)

        return newFiles

    def pathToScratchCase(self):
        """ Metodo que sirve para obtener la ruta del caso en scratch
        """
        scratchPath = os.path.abspath(self.scratchPath)
        basename = os.path.basename(self.newname)
        path = os.path.join(scratchPath, basename + "-" + self.vulType + "/")
        return path

    def setPan(self, path):
        scratchCasePath = self.pathToScratchCase()
        newname = self.newname + ".pan"
        newfilePath = os.path.join(scratchCasePath, newname)
        os.makedirs(os.path.dirname(newfilePath), exist_ok=True)
        copyfile(path, newfilePath)
        return

    def pathToPos(self):
        """ Metodo que sirve para obtener la ruta del archivo pos
        """
        casePath = self.pathToScratchCase()
        basename = os.path.basename(self.newname)
        posPath = os.path.join(casePath, basename + ".pos")
        return posPath

    def pathToFan(self):
        """ Metodo que sirve para obtener la ruta del archivo fan
        """
        casePath = self.pathToScratchCase()
        basename = os.path.basename(self.newname)
        fanPath = os.path.join(casePath, basename + ".fan")
        return fanPath


    # TODO private
    def _create(self, parameters):
        """ Metodo que copia el archivo base y reemplaza con sed

        Parameters
        ----------
        dictParameters:
            Diccionario con los parametros de lmfit
        otherParams:
            Diccionario opcional para agregar otros parametros
        """
        self._runned = False
        textToSed = ""
        for name, value in parameters.items():
                textToSed += '; s/'
                textToSed += "%" + name + "%/"
                textToSed += self._formatingNumbers(name, value)
                textToSed += "/g"

        # newfilePath = self._copyToNewDir()
        # print("LO QUE SE ENVIA A SED")
        # print(textToSed, newfilePath)
        # print("text to sed: ", textToSed)
        # print("newfilePath", newfilePath)
        # subprocess.call(["sed", "-i", "-e", textToSed, newfilePath])

        newFiles = self._copyToNewDir()
        for ifile in newFiles:
            subprocess.call(["sed", "-i", "-e", textToSed, ifile])

        return newFiles

    def run(self, parameters, *args, **kwargs):
        """ Metodo que corre el caso vulcan
        """
        stdout_redirects.redirect()

        self._runned = False
        self._create(parameters)
        # stdout_redirects.redirect()

        newname = self.newname + '.dat'
        scratchPath = os.path.abspath(self.scratchPath)
        newfilePath = os.path.abspath(self.folderTemp)
        newfilePath = os.path.join(newfilePath, newname)
        caseData = [self.vulType, newfilePath]
        case = Vulcan(scratchPath, caseData)
        case.run()
        self._runned = True
        # stdout_redirects.stop_redirect()
        stdout_redirects.stop_redirect()
        return self.result()


    def result(self):
        if self._runned:
            posFile = self.pathToPos()
            vulcanResult = VulcanPosMesh(posFile, VulcanPosMesh.MECHANICAL)
        else:
            raise Exception("Case has not run")
        return vulcanResult

    def makeCleans(self):
        return
