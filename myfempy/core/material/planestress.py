import numpy as np

INT32 = np.uint32
FLT64 = np.float64

from myfempy.core.material.material import Material


class PlaneStress(Material):
    """Plane Stress Isotropic Material Class <ConcreteClassService>"""

    def getMaterialSet():
        matset = {
            "mat": "planestress",
            "type": "isotropic",
        }
        return matset

    def getElasticTensor(tabmat, inci, element_number, Model=None):
        # material elasticity
        E = tabmat[int(inci[element_number, 2]) - 1]["EXX"]
        # material poisson ratio
        v = tabmat[int(inci[element_number, 2]) - 1][ "VXY"]  
        
        D = np.zeros((3, 3), dtype=FLT64)
        D[0, 0] = E / (1.0 - v * v)
        D[0, 1] = D[0, 0] * v
        D[1, 0] = D[0, 1]
        D[1, 1] = D[0, 0]
        D[2, 2] = E / (2.0 * (1.0 + v))
        return D

    def getElementStrain(Model, U, ptg, element_number):
        elem_set = Model.element.getElementSet()
        nodedof = len(elem_set["dofs"]["d"])

        nodelist = Model.shape.getNodeList(Model.inci, element_number)

        loc = Model.shape.getLocKey(nodelist, nodedof)

        elementcoord = Model.shape.getNodeCoord(Model.coord, nodelist)
        
        diffN = Model.shape.getDiffShapeFuntion(np.array([ptg, ptg]), nodedof)
        
        invJ = Model.shape.getinvJacobi(np.array([ptg, ptg]), elementcoord, nodedof)

        B = Model.element.getB(diffN, invJ)

        epsilon = B.dot(U[loc]) #np.dot(B, U[loc])  # B @ (U[loc])

        strn_elm_xx = epsilon[0]
        
        strn_elm_yy = epsilon[1]
        
        strn_elm_xy = epsilon[2]

        # T = np.array([[1.0, -0.5, 0.0],
        #               [-0.5, 1.0, 0.0],
        #               [0.0, 0.0, 3.0]])
        # strain = np.array([strn_elm_xx, strn_elm_yy, strn_elm_xy])
        # strn_elm_vm = np.sqrt(np.dot(strain.transpose() ,np.dot(T, strain)))

        strn_elm_vm = np.sqrt(
            epsilon[0] ** 2
            - epsilon[0] * epsilon[1]
            + epsilon[1] ** 2
            + 3 * epsilon[2] ** 2
        )

        strain = [strn_elm_vm, strn_elm_xx, strn_elm_yy, strn_elm_xy]

        return epsilon, strain

    def getTitleStrain():
        title = ["STRAIN_VM", "STRAIN_XX", "STRAIN_YY", "STRAIN_XY"]
        return title

    def getElementStress(Model, epsilon, element_number):

        #PlaneStress.getElasticTensor(E, v)
        C = Model.material.getElasticTensor(Model.tabmat, Model.inci,  element_number)

        sigma = C.dot(epsilon) #np.dot(C, epsilon)

        strs_elm_xx = sigma[0]
        
        strs_elm_yy = sigma[1]
        
        strs_elm_xy = sigma[2]

        strs_elm_vm = np.sqrt(
            sigma[0] ** 2 - sigma[0] * sigma[1] + sigma[1] ** 2 + 3 * sigma[2] ** 2
        )

        stress = [strs_elm_vm, strs_elm_xx, strs_elm_yy, strs_elm_xy]

        return sigma, stress

    def getTitleStress():
        title = ["STRESS_VM", "STRESS_XX", "STRESS_YY", "STRESS_XY"]
        return title

    def getStrainEnergyDensity(sigma, epsilon, elemvol):
        strain_energy = 0.5 * np.dot(sigma.transpose(), epsilon) / elemvol
        return strain_energy

    def getTitleCompliance():
        title = ["STRAIN_ENERGY_DENSITY"]
        return title

    def getFailureCriteria(sigma):
        return 0.0

    def getTitleFoS():
        title = ["FoS_YIELD_VON_MISES"]
        return title

    def getStrainMechanical(strain_vector):
        strain = np.zeros((3, strain_vector.shape[0]))
        strain[0, :] = strain_vector
        strain[1, :] = strain_vector
        return  strain
    
    def getStrainThermal(strain_vector):
        strain = np.zeros((3, strain_vector.shape[0]))
        strain[0, :] = strain_vector
        strain[1, :] = strain_vector
        return  strain