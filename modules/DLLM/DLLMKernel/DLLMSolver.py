# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: iso-8859-1 -*-
# Copyright: Airbus
# @version: 1.0
# @author: Fran�ois Gallard
# @author: Matthieu MEAUX (for refactoring)
 
# - Local imports -
from DLLM.DLLMKernel.DLLMMesh import DLLMMesh
from DLLM.DLLMKernel.DLLMDirect import DLLMDirect
from DLLM.DLLMKernel.DLLMPost import DLLMPost
from DLLM.DLLMKernel.DLLMAdjoint import DLLMAdjoint

class DLLMSolver:
    ERROR_MSG='ERROR in DLLMSolver.'
    def __init__(self, wing_geom, airfoils, OC):
        '''
        Constructor for wings based on lifting line theory
        @param wing_geom : the wing geometry
        @param Lref : Reference length for the moments computation
        @param relaxFactor : relaxation factor for induced angles computation
        @param stopCriteria : the stop criteria for the iterative method for computing the wing circulation.
        '''
        
        self.__wing_geom  = wing_geom
        self.__airfoils   = airfoils
        self.__OC         = OC
        
        self.__Lref       = 0.
        self.__Sref       = 0.
        
        self.__DLLMMesh   = DLLMMesh(self)
        self.__DLLMDirect = DLLMDirect(self)
        self.__DLLMPost   = DLLMPost(self)
        self.__DLLMAdjoint= DLLMAdjoint(self)
        
        self.set_OC(OC)
    
    #-- Accessors
    def get_wing_geom(self):
        return self.__wing_geom
    
    def get_airfoils(self):
        return self.__airfoils
    
    def get_OC(self):
        return self.__OC
    
    def get_Lref(self):
        return self.__Lref
    
    def get_Sref(self):
        return self.__Sref
    
    #-- DLLMMesh accessors
    def get_K(self):
        return self.__DLLMMesh.get_K()
    
    #-- DLLMDirect accessors
    def is_direct_computed(self):
        return self.__DLLMDirect.is_computed()
    
    def get_convergence_history(self):
        return self.__DLLMDirect.get_convergence_history()
    
    def get_localAoA(self):
        return self.__DLLMDirect.get_localAoA()
    
    def get_iAoA(self):
        return self.__DLLMDirect.get_iAoA()
    
    def get_R(self):
        return self.__DLLMDirect.get_R()
    
    def get_DR_DiAoA(self):
        return self.__DLLMDirect.get_DR_DiAoA()
    
    def get_DR_DTwist(self):
        return self.__DLLMDirect.get_DR_DTwist()
    
    def get_DR_DAoA(self):
        return self.__DLLMDirect.get_DR_DAoA()
    
    def get_DR_DThickness(self):
        return self.__DLLMDirect.get_DR_DThickness()
    
    def get_DlocalAoA_DiAoA(self):
        return self.__DLLMDirect.get_DlocalAoA_DiAoA()
    
    def get_DlocalAoA_DTwist(self):
        return self.__DLLMDirect.get_DlocalAoA_DTwist()
    
    def get_DlocalAoA_DAoA(self):
        return self.__DLLMDirect.get_DlocalAoA_DAoA()
    
    #-- DLLMPost accessors
    def is_post_computed(self):
        return self.__DLLMPost.is_computed()
    
    def get_func_list(self):
        return self.__DLLMPost.get_func_list()
    
    def get_dfunc_diAoA(self):
        return self.__DLLMPost.get_dfunc_diAoA()
    
    def get_dpJ_dpTwist(self):
        return self.__DLLMPost.get_dpJ_dpTwist()
    
    def get_dpJ_dpAoA(self):
        return self.__DLLMPost.get_dpJ_dpAoA()
    
    def get_dpJ_dpThickness(self):
        return self.__DLLMPost.get_dpJ_dpThickness()
     
    #-- Setters
    def __reinit_modules(self):
        self.__DLLMDirect.set_computed(False)
        self.__DLLMPost.set_computed(False)
        self.__DLLMAdjoint.set_computed(False)
        
    def set_OC(self, OC):
        self.__OC = OC
        self.__reinit_modules()
        
    def set_wing_geom(self, wing_geom):
        self.__wing_geom  = wing_geom
        self.__DLLMMesh.recompute()
        self.__reinit_modules()
        
    def set_airfoil(self, airfoils):
        self.__airfoils = airfoils
        self.__DLLMMesh.recompute()
        self.__reinit_modules()
        
    def set_Lref(self, Lref):
        self.__Lref = Lref
        
    def set_Sref(self, Sref):
        self.__Sref = Sref
    
    #-- DLLMDirect setters
    def set_relax_factor(self, relax_factor):
        self.__DLLMDirect.set_relax_factor(relax_factor)
        
    def set_stop_criteria(self, residual=None, n_it=None):
        self.__DLLMDirect.set_stop_criteria(residual=residual, n_it=n_it)
        
    def set_gamma_file_name(self, gamma_f_name):
        self.__DLLMDirect.set_gamma_file_name(gamma_f_name)
        
    #-- Run methods
    def run_direct(self):
        self.__DLLMDirect.run()
        
    def run_post(self,func_list=None):
        ERROR_MSG=self.ERROR_MSG+'run_post: '
        if self.is_direct_computed():
            self.__DLLMPost.run(func_list=func_list)
        else:
            print ERROR_MSG+'Cannot run post-processing if solution is not computed'
            
    def run_adjoint(self):
        ERROR_MSG=self.ERROR_MSG+'run_adjoint: '
        if self.is_post_computed():
            self.__DLLMAdjoint.run()
        else:
            print ERROR_MSG+'Cannot run adjoint if post-processing is not computed'       
    