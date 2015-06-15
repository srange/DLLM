"""
@author Francois Gallard
"""

# pylint: disable-msg=E0611,F0401
from openmdao.main.api import Component
from openmdao.main.datatypes.api import Float, Array
from DLLM.DLLMGeom.wing_param import Wing_param
from DLLM.DLLMKernel.DLLMTargetLift import DLLMTargetLift
from MDOTools.OC.operating_condition import OperatingCondition
import numpy as np


class DLLMOpenMDAOComponent(Component):
    # set up interface to the framework
    # pylint: disable-msg=E1101
    # Outputs of lifting line problem
    """OpenMDAO component for DLLM implementation
    """
    Lift = Float(iotype='out', desc='Lift')
    Drag = Float(iotype='out', desc='Drag')
    Drag_Pressure = Float(iotype='out', desc='Drag_Pressure')
    Drag_Induced = Float(iotype='out', desc='Drag_Induced')
    Drag_Wave = Float(iotype='out', desc='Drag_Wave')
    Drag_Friction = Float(iotype='out', desc='Drag_Friction')
    Cd = Float(iotype='out', desc='Cd')
    Cdp = Float(iotype='out', desc='Cdp')
    Cdi = Float(iotype='out', desc='Cdi')
    Cdw = Float(iotype='out', desc='Cdw')
    Cdf = Float(iotype='out', desc='Cdf')
    Cl = Float(iotype='out', desc='Cl')
    LoD = Float(iotype='out', desc='LoD')
    Sref = Float(iotype='out', desc='Sref')

    # Design variables of lifting line problem
    rtwist = Array([], desc='rtwist', iotype="in")
    span = Float(desc='span', default_value=34.1, iotype="in")
    sweep = Float(desc='sweep', default_value=34., iotype="in")
    break_percent = Float(desc='break_percent', default_value=33., iotype="in")
    root_chord = Float(desc='root_chord', default_value=6.1, iotype="in")
    break_chord = Float(desc='break_chord', default_value=4.6, iotype="in")
    tip_chord = Float(desc='tip_chord', default_value=1.5, iotype="in")
    root_height = Float(desc='root_height', default_value=1.28, iotype="in")
    break_height = Float(desc='break_height', default_value=0.97, iotype="in")
    tip_height = Float(desc='tip_height', default_value=0.33, iotype="in")
    # Operating conditions variables
    Mach = Float(iotype='in', default_value=0.7, desc='Mach')
    altitude = Float(iotype='in', default_value=0., desc='Altitude')
    T0 = Float(iotype='in', default_value=OperatingCondition.T0, desc='Ground ISA ref Temperature')
    P0 = Float(iotype='in', default_value=OperatingCondition.P0, desc='Ground ISA ref Pressure')

    def __init__(self, N, verbose=0):
        """Initialization of DLLM component.
        DLLM component use target lift capability of DLLM kernel
        Inputs :
            - N : integer. Number of discrete section on 1/2 wing
            - verbose : integer : verbosity level
        """
        self.N = N
        self.OC = None
        self.rtwist = np.zeros(N)
        self.__display_wing_param = True
        self.__verbose = verbose
        self.wing_param = None
        super(DLLMOpenMDAOComponent, self).__init__()
        self.__set_OC(OC_name="LLW_OC")
        self.__set_wing_param()
        self.DLLM = DLLMTargetLift('test', self.wing_param,
                                   self.OC, verbose=self.__verbose)
        self.DLLM.run_direct()
        self.DLLM.run_post()

    def __set_wing_param(self, wing_param_name='test_param'):
        """Method for wing parameters setting : design variables initial values and bounds"""
        self.__set_wing_param_values(wing_param_name=wing_param_name)

        self.__set_wing_param_bounds()
        self.wing_param.build_linear_airfoil(
            self.OC, AoA0=-2., Cm0=-0.1, set_as_ref=True)
        self.wing_param.build_airfoils_from_ref()
        self.wing_param.update()

        if self.__display_wing_param:
            self.__display_wing_param = False
            print self.wing_param

    def __set_wing_param_values(self, wing_param_name='test_param'):
        """Method for wing parameters variables setting""" 
        self.wing_param = Wing_param(wing_param_name,
            geom_type='Broken', n_sect=self.N * 2)
        self.wing_param.build_wing()
        for param in Wing_param.DISCRETE_ATTRIBUTES_LIST:
            self.wing_param.set_value(param, eval('self.%s' % param))

    def __set_wing_param_bounds(self):
        """Method for desing variables bounds settings
        Values are set to inf/-inf in DLLM component and their 'real' bounds
        are defined when optimization problem is set 
        """
        for i in xrange(self.N):
            self.wing_param.convert_to_design_variable(
#                'rtwist%s' % i, (-float('inf'), float('inf')))
                'rtwist%s' % i, (-float('inf'), float('inf')))
        for param in Wing_param.DISCRETE_ATTRIBUTES_LIST:
            self.wing_param.convert_to_design_variable(
                param, (-float('inf'), float('inf')))
        return

    def __set_OC(self, OC_name='OC1'):
        """ Set default operating conditions"""
        self.OC = OperatingCondition(OC_name, atmospheric_model='ISA')
        self.OC.set_Mach(self.Mach)
        self.OC.set_altitude(self.altitude)
        self.OC.set_T0(self.T0)
        self.OC.set_P0(self.P0)
        self.OC.set_humidity(1.)
        self.OC.compute_atmosphere()

    def execute(self):
        """ Perform a DLLM computation with the """
        for dv_id in self.wing_param.get_dv_id_list():
            if dv_id.startswith('rtwist'):
                i_twist = int(dv_id.replace('rtwist', ''))
                self.wing_param.set_value(dv_id, self.rtwist[i_twist])
            else:
                exec("self.wing_param.set_value('%s',float(self.%s))" %
                     (dv_id, dv_id))
        self.wing_param.update()
        self.__set_OC()
        self.DLLM.run_direct()
        self.DLLM.run_post()
        output = self.DLLM.get_F_list()
        for f, f_name in zip(output, self.DLLM.get_F_list_names()):
            exec("self." + f_name + "=" + str(f))

    def list_deriv_vars(self):
        """specify the inputs and outputs where derivatives are defined
        Specific treatment for twist : defined as rtwist0, rtwist1,... in DLLM
        but as an array rtwist in openmdao component"""

        out_dvid = []
        for dv_id in self.wing_param.get_dv_id_list():
            if dv_id.startswith('rtwist0'):
                out_dvid.append('rtwist')
            elif not dv_id.startswith('rtwist'):
                out_dvid.append(dv_id)
        return tuple(out_dvid), tuple(self.DLLM.get_F_list_names())

    def provideJ(self):
        """Calculate the Jacobian according inputs and outputs"""
        self.DLLM.run_adjoint()
        return np.array(self.DLLM.get_dF_list_dchi())

# if __name__ == "__main__":
#     import time
#     tt = time.time()
#     N = 20
#     DLLMOpenMDAO = DLLMOpenMDAOComponent(N, verbose=1)
#     DLLMOpenMDAO.OC.set_altitude(190000.)
#     DLLMOpenMDAO.DLLM.set_target_Lift(606570.049598)
#     DLLMOpenMDAO.run()
# 
#     print "Final point :"
#     print "    -lift :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Lift()
#     print "    -total drag :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Drag()
#     print "    -induced drag :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Drag_Induced()
#     print "    -wave drag :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Drag_Pressure()
#     print "    -wave drag :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Drag_Wave()
#     print "    -friction drag :", DLLMOpenMDAO.DLLM.get_DLLMPost().get_Drag_Friction()
