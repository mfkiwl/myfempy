from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from myfempy.core.mesh.mesh import getMesh
# from myfempy.core.solver import getSolver
from myfempy.core.elements.element import getElement
from myfempy.core.geometry.geometry import getGeometry
from myfempy.core.material.material import getMaterial
from myfempy.core.shapes.shape import getShape
from myfempy.plots.prevplot import preview_plot
from myfempy.setup.model import SetModel
from myfempy.setup.physics import SetPhysics
from myfempy.setup.results import setPostProcess
from myfempy.io.path import newDir

import sys
import logging
from time import time

class newAnalysis():
    """
    newAnalysis new analysis from fe model to simulation
    """
    def __init__(self, FEASolver) -> None:
        self.solver = FEASolver
        self.path  = newDir('out')
        logging.basicConfig(filename=str(self.path)+ "/" +'myfempy_log.log', encoding='utf-8', level=logging.DEBUG, filemode="w")
        
    def Model(self, modeldata):
        """
        Model finite element model set 

        Arguments:
            modeldata -- data information
        """
        try:     
            Mesh = newAnalysis.setMesh(modeldata)
            logging.info('TRY SET MESH -- SUCCESS')
        except:
            logging.warning('TRY SET MESH -- FAULT')
            sys.exit()
        try:     
            Shape = newAnalysis.setShape(modeldata)
            logging.info('TRY SET SHAPE -- SUCCESS')
        except:
            logging.warning('TRY SET SHAPE -- FAULT')
        try:     
            Element = newAnalysis.setElement(modeldata)
            logging.info('TRY SET ELEMENT -- SUCCESS')
        except:
            logging.warning('TRY SET ELEMENT -- FAULT')
        try:     
            Material = newAnalysis.setMaterial(modeldata)
            logging.info('TRY SET MATERIAL -- SUCCESS')
        except:
            logging.warning('TRY SET MATERIAL -- FAULT')
        try:     
            Geometry = newAnalysis.setGeometry(modeldata)
            logging.info('TRY SET GEOMETRY -- SUCCESS')
        except:
            logging.warning('TRY SET GEOMETRY -- FAULT')
        try:     
            self.model = SetModel(Mesh, Element, Shape, Material, Geometry)
            self.model.modeldata = modeldata
            logging.info('TRY SET FEMODEL -- SUCCESS')
        except:
            logging.warning('TRY SET FEMODEL -- FAULT')
        # self.model.element = Element
        # self.model.shape = Shape
        # self.model.material = Material
        # self.model.geoemtry = Geometry
        # self.inci = FEANewAnalysis.getInci(self)
        # self.coord = FEANewAnalysis.getCoord(self)
        # self.tabmat = FEANewAnalysis.getTabmat(self)
        # self.tabgeo = FEANewAnalysis.getTabgeo(self)
        # self.intgauss = FEANewAnalysis.getIntGauss(self)
        self.modelinfo = dict()
        self.modelinfo['inci'] = newAnalysis.getInci(self)
        self.modelinfo['coord'] = newAnalysis.getCoord(self)
        self.modelinfo['tabmat'] = newAnalysis.getTabmat(self)
        self.modelinfo['tabgeo'] = newAnalysis.getTabgeo(self)
        self.modelinfo['intgauss'] = newAnalysis.getIntGauss(self)
        try:
            self.modelinfo["regions"] = self.model.mesh.getRegionsList(self.model.mesh.getElementConection(self.model.modeldata['MESH']))
        except:
            self.modelinfo["regions"] = []
        elem_set = self.model.element.getElementSet()
        self.modelinfo['tensor'] = len(elem_set['tensor'])
        self.modelinfo['dofs'] = elem_set["dofs"]
        self.modelinfo['nodedof'] = len(elem_set["dofs"]['d'])
        self.modelinfo['type_element'] = elem_set["key"]
        shape_set = self.model.shape.getShapeSet()
        self.modelinfo["shapeid"] = shape_set['id']
        self.modelinfo['nodecon'] =  len(shape_set['nodes'])
        self.modelinfo['elemdofs'] = len(shape_set['nodes'])*self.modelinfo['nodedof']
        self.modelinfo['type_shape'] = shape_set["key"]
        self.modelinfo["elemid"] = int(f'{elem_set["id"]}{shape_set["id"]}') #elem_set['id']
        self.modelinfo['nnode'] = len(self.model.coord)
        self.modelinfo['nelem'] = len(self.model.inci)
        self.modelinfo['fulldofs'] = len(elem_set["dofs"]['d']) * len(self.model.coord)
        self.modelinfo['elemvol'] = newAnalysis.getElementVolume(self, self.modelinfo['inci'], self.modelinfo['coord'], self.modelinfo['tabgeo'], self.modelinfo['intgauss'])
        
        
    def Physic(self, physicdata):
        """
        Physic physics set load and boundary conditions

        Arguments:
            physicdata -- data information
        """
        self.modelinfo['domain'] = physicdata['DOMAIN']
        # Domain = NewAnalysis.setDomain(physicdata)
        # if "COUPLING" in physicdata.keys():
        #     coupling = NewAnalysis.setCoupling(physicdata)
        #     Domain.coupling = coupling
        # try:
        Loads, BoundCond = newAnalysis.setDomain(physicdata)
        self.physic = SetPhysics(Loads, BoundCond)
        self.physic.physicdata = physicdata
            # logging.info('TRY SET PHYSICS -- SUCCESS')
        # except:
        #     logging.warning('TRY SET PHYSICS -- FAULT')
        self.modelinfo["forces"] = newAnalysis.getLoadApply(self)
        self.modelinfo["constrains"] = newAnalysis.getBCApply(self)
        # self.loadaply = FEANewAnalysis.getLoadApply(self)
        # self.constrains = FEANewAnalysis.getBCApply(self)
        
    def Assembly(self):
        """
        Assembly assembly of fe model algebric system

        Returns:
            matrix and vector from fe model
        """
        inci = self.modelinfo['inci']
        coord = self.modelinfo['coord']
        tabmat = self.modelinfo['tabmat']
        tabgeo = self.modelinfo['tabgeo']
        intgauss = self.modelinfo['intgauss']       
            
        # try:
        matrix = newAnalysis.getGlobalMatrix(self, inci, coord, tabmat, tabgeo, intgauss) #self.solver.getMatrixAssembler(self.model, inci, coord, tabmat, tabgeo)
        logging.info('TRY RUN GLOBAL ASSEMBLY -- SUCCESS')     
        # except:
        #     logging.warning('TRY RUN GLOBAL ASSEMBLY -- FAULT')
        loadaply = newAnalysis.getLoadApply(self)
        try:
            addSpring = np.where(loadaply[:,1]==16)
            addMass = np.where(loadaply[:,1]==15)
            if addSpring[0].size:
                addLoad = loadaply[addSpring, :][0]
                print(len(addLoad))
                for ii in range(len(addLoad)):
                    A_add = addLoad[ii, 2] * np.array([[1, -1], [-1, 1]])
                    loc = np.array([int(self.modelinfo['dofe']*addLoad[ii, 0]-(self.modelinfo['dofe'])),
                                    int(self.modelinfo['dofe']*addLoad[ii, 0]-(self.modelinfo['dofe'] - 1))])
                    matrix['stiffness'] = self.solver.addMatrix(matrix['stiffness'], A_add, loc)
                logging.info('TRY RUN ADD SPRING -- SUCCESS')
            if addMass[0].size:
                addLoad = loadaply[addMass, :][0]
                for ii in range(len(addLoad)):
                    A_add = addLoad[ii, 2] * np.array([[1, -1], [-1, 1]])
                    loc = np.array([int(self.modelinfo['dofe']*addLoad[ii, 0]-(self.modelinfo['dofe'])),
                                    int(self.modelinfo['dofe']*addLoad[ii, 0]-(self.modelinfo['dofe'] - 1))])
                    matrix['mass'] = self.solver.addMatrix(matrix['mass'], A_add, loc) 
                logging.info('TRY RUN ADD MASS -- SUCCESS')
        except:
            logging.warning('TRY RUN ADD ASSEMBLY -- FAULT')           
        try:
            forcelist = newAnalysis.getLoadArray(self, loadaply)
            logging.info('TRY RUN LOAD ASSEMBLY -- SUCCESS')     
        except:
            logging.warning('TRY RUN LOAD ASSEMBLY -- FAULT')                                          
        return matrix, forcelist
    
    def Solve(self, solvedata):
        """
        runSolve run the solver set

        Arguments:
            solvedata -- data information

        Returns:
            solution 
        """
        # fulldofs = self.modelinfo['fulldofs']
        # self.modelinfo = dict()
        # self.modelinfo['coord'] = self.coord
        # self.modelinfo['regions'] = self.regions
        solvedata["solverstatus"] = dict()
        starttime = time()
        assembly, forcelist = newAnalysis.Assembly(self)
        endttime = time()
        solvedata["solverstatus"]["timeasb"] = abs(endttime - starttime)
        solvedata["solverstatus"]["memorysize"] = assembly['stiffness'].data.nbytes    
        constrains = newAnalysis.getBCApply(self)
        try:
            freedof, fixedof = newAnalysis.getConstrains(self, constrains)
            logging.info('TRY RUN CONSTRAINS -- SUCCESS')
        except:
            logging.warning('TRY RUN CONSTRAINS -- FAULT')
        # forcelist = FEANewAnalysis.getLoadArray(self)
        try:
            starttime = time()
            solvedata['solution'] = self.solver.runSolve(self.modelinfo['fulldofs'], assembly, forcelist, freedof, solvedata)
            endttime = time()
            solvedata["solverstatus"]["timesim"] = abs(endttime - starttime)
            logging.info('TRY RUN SOLVER -- SUCCESS') 
        except:
            logging.warning('TRY RUN SOLVER -- FAULT')
        return solvedata
    

    def PreviewAnalysis(self, previewdata):
        """
        PreviewAnalysis preview the model+physic set

        Arguments:
            previewdata -- data information
        """
        # modelinfo = dict()
        # modelinfo["coord"] = self.coord   #FEANewAnalysis.getCoord(self)
        # modelinfo["inci"] = self.inci     #FEANewAnalysis.getInci(self)
        # modelinfo["tabgeo"] = self.tabgeo #FEANewAnalysis.getTabgeo(self)
        # shape_set = self.model.shape.getShapeSet()
        # elem_set = self.model.element.getElementSet()
        # self.modelinfo["nodecon"] = len(shape_set['nodes'])
        # self.modelinfo["elemid"] = elem_set['id']
        # try:
        #     self.regions = self.model.mesh.getRegionsList(self.model.mesh.getElementConection(self.model.modeldata['MESH']))
        # except:
        #     self.regions = []
        # modelinfo["regions"] = self.regions
        # try:
        #      modelinfo["forces"] = FEANewAnalysis.getLoadApply(self)
        # except:
        #     pass
        #     # modelinfo["forces"] = []
        # try:
        #     modelinfo["constrains"] = FEANewAnalysis.getBCApply(self)
        # except:
        #     pass
        #     modelinfo["constrains"] = []
        # modelinfo["forces"] = FEANewAnalysis.getLoadApply(self)
        # modelinfo["constrains"] = FEANewAnalysis.getBCApply(self)
        try:
            path=str(self.path)
            preview_plot(previewdata, self.modelinfo, path)
            logging.info('TRY RUN PREVIEW PLOT -- SUCCESS')
        except:
            logging.warning('TRY RUN PREVIEW PLOT -- FAULT')
     

    def PostProcess(self, postprocdata):
        """
        PostProcess prost process the solution

        Arguments:
            postprocdata -- data information

        Returns:
            post process arrays 
        """
        postporc_result = []
        try:
            if "COMPUTER" in postprocdata.keys(): 
                postporc_result = setPostProcess.getCompute(self, postprocdata)
            if "TRACKER" in postprocdata.keys():
                setPostProcess.getTracker(self, postprocdata, postporc_result)
            if "OUTPUT" in postprocdata.keys():
                postporc_result["log"] = []
                log_file = setPostProcess.getLog(self, postprocdata, postporc_result)
                postporc_result["log"].append(log_file)
            logging.info('TRY GET POST PROCESS -- SUCCESS')        
        except:
            logging.warning('TRY GET POST PROCESS -- FAULT')
        return postporc_result
                
                
    # seting
    def setMesh(modeldata):
        set_mesh = dict()
        set_mesh = modeldata['MESH']
        # set_mesh['type'] = modeldata['MESH']['TYPE'] 
        set_mesh['shape'] = modeldata['ELEMENT']['SHAPE']
        return getMesh(set_mesh)
    
    def setShape(modeldata):
        set_shape = dict()
        set_shape['type'] = modeldata['ELEMENT']['SHAPE']
        return getShape(set_shape)
    
    def setElement(modeldata):
        set_element = dict()
        set_element['type'] = modeldata['ELEMENT']['TYPE']
        return getElement(set_element)
    
    def setMaterial(modeldata):
        set_material = dict()
        set_material['mat'] = modeldata['MATERIAL']['MAT']
        set_material['type'] = modeldata['MATERIAL']['TYPE']
        return getMaterial(set_material)
    
    def setGeometry(modeldata):
        set_geometry = dict()
        set_geometry['geo'] = modeldata['GEOMETRY']['GEO']
        return getGeometry(set_geometry)
            
    
    def setDomain(physicdata):
        if physicdata['DOMAIN'] == 'structural':
            from myfempy.core.physic.bcstruct import BoundCondStruct
            from myfempy.core.physic.loadstruct import LoadStructural
            return LoadStructural, BoundCondStruct
        else:
            pass 
    

    def setSolution(self, solvedata):
        # self.inci = FEANewAnalysis.getInci(self)
        # self.coord = FEANewAnalysis.getCoord(self)
        # self.tabmat = FEANewAnalysis.getTabmat(self)
        # self.tabgeo = FEANewAnalysis.getTabgeo(self)
        # self.intgauss = FEANewAnalysis.getIntGauss(self)
        # elem_set = self.model.element.getElementSet()
        # nodedof = len(elem_set["dofs"])
        self.solver.fulldofs = (self.modelinfo['dofs']) * len(self.modelinfo['nnode'])
        self.solver.solvedata = solvedata


    # geting    
    def getInci(self):
        return self.model.getInci(self.model.modeldata)
    
    def getCoord(self):
        return self.model.getCoord(self.model.modeldata)
    
    def getTabmat(self):
        return self.model.getTabMat(self.model.modeldata)
        
    def getTabgeo(self):
        return self.model.getTabGeo(self.model.modeldata)
    
    def getIntGauss(self):
        return self.model.setIntGauss(self.model.modeldata)
    
    def getElementVolume(self, inci, coord, tabgeo, intgauss):
        vol = np.zeros((len(inci)))
        for ee in range(len(inci)):
            vol[ee] = self.model.element.getElementVolume(self.model, inci, coord, tabgeo, intgauss, ee)
        return vol

    def getElemStifLinearMat(self, inci, coord, tabmat, tabgeo, intgauss, element_number):        
        return self.model.element.getStifLinearMat(self.model, inci, coord, tabmat, tabgeo, intgauss, element_number)
         
    def getElemMassConsistentMat(self, inci, coord, tabmat, tabgeo, intgauss, element_number):        
        return self.model.element.getMassConsistentMat(self.model, inci, coord, tabmat, tabgeo, intgauss, element_number)
                     
    def getGlobalMatrix(self, inci, coord, tabmat, tabgeo, intgauss):
        return self.solver.getMatrixAssembler(self.model, inci, coord, tabmat, tabgeo, intgauss)
    
    def getForceList(self):
        return self.physic.getForceList(self.physic.physicdata)
    
    def getBoundCondList(self):
        return self.physic.getBoundCondList(self.physic.physicdata)
    
    def getLoadApply(self):
        # coord = FEANewAnalysis.getCoord(self)
        return self.physic.getLoadApply(self.physic.physicdata, self.modelinfo)
    
    def getBCApply(self):
        # coord = FEANewAnalysis.getCoord(self)
        return self.physic.getBoundCondApply(self.physic.physicdata, self.modelinfo)
        
    def getConstrains(self, constrains):
        # coord = FEANewAnalysis.getCoord(self) 
        # constrains = FEANewAnalysis.getBCApply(self)
        nodetot = len(self.modelinfo['coord'])
        # elem_set = self.model.element.getElementSet()
        # nodedof = len(elem_set["dofs"])
        freedof, fixedof = self.solver.getConstrains(constrains, nodetot, self.modelinfo['nodedof'])
        return freedof, fixedof
    
    def getLoadArray(self, loadaply):
        # coord = FEANewAnalysis.getCoord(self)     
        nodetot = len(self.modelinfo['coord'])
        # elem_set = self.model.element.getElementSet()
        # nodedof = len(elem_set["dofs"])
        # loadaply = FEANewAnalysis.getLoadApply(self)    
        loadvec = self.solver.getLoadAssembler(loadaply, nodetot, self.modelinfo['nodedof'])
        return loadvec