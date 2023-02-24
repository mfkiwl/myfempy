#!/usr/bin/env python
from myfempy.felib.materset import get_elasticity
import numpy as np

__doc__ = """
spring21.py: Spring 2D 2-node linear Finite Element
"""


class Spring21:
    """class Spring 2D 2-node linear Finite Element"""

    def __init__(self, modelinfo):
        self.dofe = modelinfo["nodecon"][0] * modelinfo["nodedof"][0]
        self.fulldof = modelinfo["nodedof"][0] * len(modelinfo["coord"])
        self.nodedof = modelinfo["nodedof"][0]
        self.nelem = len(modelinfo["inci"])
        self.nnode = len(modelinfo["coord"])
        self.inci = modelinfo["inci"]
        self.coord = modelinfo["coord"]
        self.tabmat = modelinfo["tabmat"]
        self.tabgeo = modelinfo["tabgeo"]
        
        """
        Arguments:
           modelinfo:dict     -- F.E. model dict with full information needed

        Parameters:
            dofe              -- element dof
            fulldof           -- total dof of model
            nodedof           -- node dof 
            nelem             -- total number of elements in mesh
            nnode             -- number of degree of freedom per node
            inci              -- elements conection and prop. list
            coord             -- nodes coordinates list in mesh
            tabmat            -- table of material prop.
            tabgeo            -- table of geometry prop.
            
        """  

    @staticmethod
    def elemset():
        """element setting"""
        
        dofelem = {
            "key": "spring21",
            "id": 110,
            "def": "struct 1D",
            "dofs": ["ux", "uy"],
            "nnodes": ["i", "j"],
            "tensor": ["None"],
        }
        return dofelem

    def lockey(self, list_node):
        """element lockey(dof)"""
        
        noi = list_node[0]
        noj = list_node[1]
        loc = np.array(
            [
                self.nodedof * noi - 2,
                self.nodedof * noi - 1,
                self.nodedof * noj - 2,
                self.nodedof * noj - 1,
            ]
        )
        return loc

    def stiff_linear(self, ee):
        """stiffness linear matrix"""
        
        noi = int(self.inci[ee, 4])
        noj = int(self.inci[ee, 5])
        noix = self.coord[noi - 1, 1]
        noiy = self.coord[noi - 1, 2]
        nojx = self.coord[noj - 1, 1]
        nojy = self.coord[noj - 1, 2]
        D = get_elasticity(self.tabmat, self.inci, ee)
        S = D[0]
        L = np.sqrt((nojx - noix) ** 2 + (nojy - noiy) ** 2)
        s = (nojy - noiy) / L
        c = (nojx - noix) / L
        T = np.zeros((self.dofe, self.dofe))
        T[0, 0] = c
        T[0, 1] = s
        T[1, 0] = -s
        T[1, 1] = c
        T[2, 2] = c
        T[2, 3] = s
        T[3, 2] = -s
        T[3, 3] = c
        kes0 = np.zeros((self.dofe, self.dofe))
        kes0[0, 0] = 1.0
        kes0[0, 2] = -1.0
        kes0[2, 0] = -1.0
        kes0[2, 2] = 1.0
        kes2 = S * kes0
        kes2T = np.dot(np.dot(np.transpose(T), kes2), T)
        list_node = [noi, noj]
        loc = Spring21.lockey(self, list_node)
        return kes2T, loc

    def mass(self, ee):
        """consistent mass matrix"""
        
        noi = int(self.inci[ee, 4])
        noj = int(self.inci[ee, 5])
        R = self.tabmat[int(self.inci[ee, 2] - 1), 6]
        mes2 = R * np.eye(self.dofe)
        list_node = [noi, noj]
        loc = Spring21.lockey(self, list_node)
        return mes2, loc


if __name__ == "__main__":
    import doctest

    doctest.testmod()
