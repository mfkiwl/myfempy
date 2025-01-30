from __future__ import annotations

import numpy as np
from scipy.special import roots_legendre

from myfempy.core.physic.thermal import Thermal
from myfempy.core.utilities import (gauss_points, get_elemen_from_nodelist,
                                    get_nodes_from_list, poly_area)


class LoadThermal(Thermal):
    """Thermal Load Class <ConcreteClassService>"""

    def getLoadApply(Model, modelinfo, forcelist):
        forcenodeaply = np.zeros((1, 4))

        # if forcelist['TYPE'] == "forcenode":
        #     fapp = LoadThermal.__ForceNodeLoadApply(modelinfo, forcelist)
        #     forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        if forcelist["TYPE"] == "heatfluxedge":
            fapp = LoadThermal.__ForceEdgeLoadApply(Model, modelinfo, forcelist)
            forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        # elif forcelist['TYPE'] == "heatfluxesurf":
        #     fapp = LoadThermal.__ForceSurfLoadApply(modelinfo, forcelist)
        #     forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        elif forcelist["TYPE"] == "convectionedge":
            fapp = LoadThermal.__ForceEdgeLoadApply(Model, modelinfo, forcelist)
            forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        # elif forcelist['TYPE'] == "convectionsurf":
        #     fapp = LoadThermal.__ForceEdgeLoadApply(Model, modelinfo, forcelist)
        #     forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        elif forcelist["TYPE"] == "heatgeneration":
            fapp = LoadThermal.__ForceBodyLoadApply(Model, modelinfo, forcelist)
            forcenodeaply = np.append(forcenodeaply, fapp, axis=0)

        else:
            pass

        forcenodeaply = forcenodeaply[1::][::]
        return forcenodeaply

    def getUpdateMatrix(Model, matrix, loadaply):

        addConv = np.where(loadaply[:, 1] == 15)

        if addConv[0].size:
            addLoad = loadaply[addConv, :][0]
            matrix["stiffness"] = Model.element.getUpdateMatrix(
                Model, matrix["stiffness"], addLoad
            )
        return matrix

    def getUpdateLoad(self):
        return None

    def __ForceNodeLoadApply(modelinfo, forcelist):
        forcenodedof = np.zeros((1, 4))
        nodelist = [
            forcelist["DIR"],
            forcelist["LOCX"],
            forcelist["LOCY"],
            forcelist["LOCZ"],
            forcelist["TAG"],
        ]
        node_list_fc, dir_fc = get_nodes_from_list(
            nodelist, modelinfo["coord"], modelinfo["regions"]
        )
        force_value_vector = np.ones_like(node_list_fc) * float(forcelist["VAL"])
        fc_type_dof = modelinfo["dofs"]["f"][forcelist["DOF"]] * np.ones_like(
            node_list_fc
        )
        for j in range(len(node_list_fc)):
            fcdof = np.array(
                [
                    [
                        int(node_list_fc[j]),
                        fc_type_dof[j],
                        force_value_vector[j],
                        int(forcelist["STEP"]),
                    ]
                ]
            )
            forcenodedof = np.append(forcenodedof, fcdof, axis=0)
        forcenodedof = forcenodedof[1::][::]
        return forcenodedof

    def __ForceBodyLoadApply(Model, modelinfo, forcelist):
        forcenodedof = np.zeros((1, 4))
        heatgen = float(forcelist["VAL"])
        inci = modelinfo["inci"]
        coord = modelinfo["coord"]
        tabmat = modelinfo["tabmat"]
        tabgeo = modelinfo["tabgeo"]
        intgauss = modelinfo["intgauss"]
        fc_type_dof = modelinfo["dofs"]["f"][forcelist["DOF"]]
        for ee in range(inci.shape[0]):
            force_value_vector, nodelist = LoadThermal.__body_force_volumetric(
                Model,
                inci,
                coord,
                tabmat,
                tabgeo,
                intgauss,
                ee,
                heatgen,
                fc_type_dof,
            )
            for j in range(len(nodelist)):
                fcdof = np.array(
                    [
                        [
                            int(nodelist[j]),
                            fc_type_dof,
                            force_value_vector[j],
                            int(forcelist["STEP"]),
                        ]
                    ]
                )
                forcenodedof = np.append(forcenodedof, fcdof, axis=0)
        forcenodedof = forcenodedof[1::][::]
        return forcenodedof

    def __ForceEdgeLoadApply(Model, modelinfo, forcelist):
        nodelist = [
            forcelist["DIR"],
            forcelist["LOCX"],
            forcelist["LOCY"],
            forcelist["LOCZ"],
            forcelist["TAG"],
        ]  # forcelist[3:]
        node_list_fc, dir_fc = get_nodes_from_list(
            nodelist, modelinfo["coord"], modelinfo["regions"]
        )
        force_value = float(forcelist["VAL"])
        force_dirc = forcelist["DOF"]
        inci = modelinfo["inci"]
        coord = modelinfo["coord"]
        tabmat = modelinfo["tabmat"]
        tabgeo = modelinfo["tabgeo"]
        intgauss = modelinfo["intgauss"]
        fc_type = forcelist["DOF"]
        elmlist = get_elemen_from_nodelist(inci, node_list_fc)
        forcenodedof = np.zeros((1, 4))
        for ee in range(len(elmlist)):

            (
                force_value_vector,
                nodelist,
                norm,
            ) = LoadThermal.__line_force_distribuition(
                Model,
                inci,
                coord,
                tabgeo,
                intgauss,
                node_list_fc,
                elmlist[ee],
                force_value,
                fc_type,
            )

            # if len(force_value_vector) > len(nodelist):
            #     nodelist = np.repeat(nodelist, len(modelinfo["dofs"]["f"]))
            #     fc_type_dof = np.tile(
            #         [modelinfo["dofs"]["f"]["fx"], modelinfo["dofs"]["f"]["fy"]],
            #         len(modelinfo["dofs"]["f"]),
            #     )

            fc_type_dof = modelinfo["dofs"]["f"][forcelist["DOF"]] * np.ones_like(
                nodelist
            )

            for j in range(len(nodelist)):
                fcdof = np.array(
                    [
                        [
                            int(nodelist[j]),
                            fc_type_dof[j],
                            force_value_vector[j],
                            int(forcelist["STEP"]),
                        ]
                    ]
                )
                forcenodedof = np.append(forcenodedof, fcdof, axis=0)
        forcenodedof = forcenodedof[1::][::]
        return forcenodedof

    # def __ForceSurfLoadApply(modelinfo, forcelist):
    #     forcenodedof = np.zeros((1, 4))

    #     nodelist = forcelist[3:]
    #     node_list_fc, dir_fc = get_nodes_from_list(nodelist, modelinfo['coord'], modelinfo['regions'])

    #     force_value = float(forcelist[2])
    #     force_dirc = forcelist[1]

    #     force_value_vector = LoadStructural.__plane_force_distribuition(modelinfo['inci'], modelinfo['coord'], node_list_fc, force_value, force_dirc, modelinfo['elemid'], modelinfo['nodedof'])

    #     node_list_fc = np.repeat(node_list_fc, modelinfo["nodedof"], axis=0)

    #     fc_type_dof = modelinfo['dofs']['f'][forcelist[1]]*np.ones_like(node_list_fc)

    #     for j in range(len(node_list_fc)):

    #         fcdof = np.array(
    #             [[
    #                 int(node_list_fc[j]),
    #                 fc_type_dof[j],
    #                 force_value_vector[j, 0],
    #                 int(forcelist[8]),
    #                 ]])
    #         forcenodedof = np.append(forcenodedof, fcdof, axis=0)

    #     forcenodedof = forcenodedof[1::][::]
    #     return forcenodedof

    def __body_force_volumetric(
        Model,
        inci,
        coord,
        tabmat,
        tabgeo,
        intgauss,
        element_number,
        heat_gen,
        fc_type_dof,
    ):
        # body force
        elem_set = Model.element.getElementSet()
        nodedof = len(elem_set["dofs"]["d"])
        shape_set = Model.shape.getShapeSet()
        nodecon = len(shape_set["nodes"])
        type_shape = shape_set["key"]
        edof = nodecon * nodedof
        nodelist = Model.shape.getNodeList(inci, element_number)
        elementcoord = Model.shape.getNodeCoord(coord, nodelist)
        t = tabgeo[int(inci[element_number, 3] - 1)][
            "THICKN"
        ]  # tabgeo[int(inci[element_number, 3] - 1), 4]
        pt, wt = gauss_points(type_shape, intgauss)
        Q = heat_gen
        force_value_vector = np.zeros((edof, 1))
        for ip in range(intgauss):
            for jp in range(intgauss):
                detJ = Model.shape.getdetJacobi(
                    np.array([pt[ip], pt[jp]]), elementcoord
                )
                N = Model.shape.getShapeFunctions(np.array([pt[ip], pt[jp]]), nodedof)
                force_value_vector += (
                    np.dot(N.transpose(), Q) * t * abs(detJ) * wt[ip] * wt[jp]
                )
        force_value_vector = force_value_vector[np.nonzero(force_value_vector)]
        return force_value_vector, nodelist

    def __line_force_distribuition(
        Model,
        inci,
        coord,
        tabgeo,
        intgauss,
        node_list_fc,
        element_number,
        force_value,
        fc_type,
    ):
        elem_set = Model.element.getElementSet()
        nodedof = len(elem_set["dofs"]["d"])
        shape_set = Model.shape.getShapeSet()
        nodecon = len(shape_set["nodes"])
        type_shape = shape_set["key"]
        edof = nodecon * nodedof
        nodelist = Model.shape.getNodeList(inci, element_number - 1)
        elementcoord = Model.shape.getNodeCoord(coord, nodelist)
        t = tabgeo[int(inci[element_number - 1, 3] - 1)][
            "THICKN"
        ]  # tabgeo[int(inci[elem - 1, 3] - 1), 4]
        # nodes, idx_conec, __ = np.intersect1d(nodelist, node_list_fc, assume_unique=True, return_indices=True)
        test = np.in1d(nodelist, node_list_fc, assume_unique=True)
        nodes = np.array(nodelist)[test]
        idx_conec = np.where(test == True)[0]
        norm = np.zeros((2))
        q = force_value
        if len(idx_conec) < 2:
            nodes = np.repeat(nodes, 2)
            force_value_vector = np.zeros((len(nodes)))
            pass
        else:
            force_value_vector = np.zeros((len(nodes)))
            if force_value == 0:
                pass
            else:
                idx_conec = np.array2string(idx_conec)
                get_side = Model.shape.getSideAxis(
                    idx_conec[1:-1]
                )  # .__get_side_fcapp(idx_conec[1:-1])
                pt, wt = gauss_points(type_shape, intgauss)
                force_value_vector = np.zeros((edof, 1))
                for ip in range(intgauss):
                    points = Model.shape.getIsoParaSide(get_side, pt[ip])
                    N = Model.shape.getShapeFunctions(np.array(points), nodedof)
                    diffN = Model.shape.getDiffShapeFuntion(np.array(points), nodedof)
                    J = Model.shape.getJacobian(np.array(points), elementcoord)
                    detJ_e = Model.shape.getEdgeLength(J, get_side)
                    force_value_vector += (
                        np.dot(N.transpose(), q) * t * abs(detJ_e) * wt[ip]
                    )
                force_value_vector = force_value_vector[np.nonzero(force_value_vector)]
        return force_value_vector, nodes, norm
