# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: iso-8859-1 -*-
# Copyright: Airbus
# @version: 1.0
# @author: Francois Gallard
# @author: Matthieu MEAUX (for refactoring)

from numpy import zeros, dot
from numpy import sin,cos

class DLLMPost:
    def __init__(self, LLW):
        """
        Post-Processing module compatible with adjoint for DLLM
        """
        self.__LLW = LLW
        self.__func_list   = None
        self.__func_dim    = 0
        self.__func_values = None
        self.__dfunc_diAoA = None
        self.__dpJ_dpchi   = None
        self.__N           = self.get_wing_param().get_n_sect()
        self.__ndv         = self.get_wing_param().get_ndv()
        self.__computed    = False
        
    #-- computed related methods
    def is_computed(self):
        return self.__computed
    
    def set_computed(self, bool=True):
        self.__computed = bool
        
    #-- Accessors
    def get_func_list(self):
        return self.__func_list
    
    def get_func_values(self):
        return self.__func_values
    
    def get_dfunc_diAoA(self):
        return self.__dfunc_diAoA
    
    def get_dpJ_dpchi(self):
        return self.__dpJ_dpchi
    
    def get_wing_param(self):
        return self.__LLW.get_wing_param()
    
    def get_airfoils(self):
        return self.__LLW.get_airfoils()
    
    def get_OC(self):
        return self.__LLW.get_OC()
    
    def get_localAoA(self):
        return self.__LLW.get_localAoA()
    
    def get_DlocalAoA_DiAoA(self):
        return self.__LLW.get_DlocalAoA_DiAoA()
    
    def get_DlocalAoA_Dchi(self):
        return self.__LLW.get_DlocalAoA_Dchi()
    
    def get_iAoA(self):
        return self.__LLW.get_iAoA()
    
    def get_Sref(self):
        return self.__LLW.get_Sref()
    
    def get_Sref_grad(self):
        return self.__LLW.get_Sref_grad()
    
    #-- Setters 
    def set_func_list(self, func_list):
        if func_list is None:
            #func_list = ['Lift', 'Drag', 'Moment', 'Cl', 'Cd', 'Cm']
            func_list = ['Lift', 'Drag', 'Cl', 'Cd']
        self.__func_list   = func_list
        self.__func_dim    = len(func_list)
        self.__func_values = zeros(self.__func_dim)
        self.__dfunc_diAoA = zeros((self.__func_dim, self.__N))
        self.__dpJ_dpchi   = zeros((self.__func_dim,self.__ndv))
        
    #-- Run method
    def run(self, func_list=None):
        self.set_func_list(func_list)
        for i,func in enumerate(self.__func_list):
            if   func == 'Cl':
                val      = self.__Cl()
                dfdiAoA  = self.__dCl_diAoA()
                dpJdpchi = self.__dpCl_dpchi()
            elif func == 'Cd':
                val      = self.__Cd()
                dfdiAoA  = self.__dCd_diAoA()
                dpJdpchi = self.__dpCd_dpchi()
#            Moments calculation are bugged for now
#             elif func == 'Cm':
#                 val = self.__Cm()
            elif func == 'Lift':
                val      = self.__Lift()
                dfdiAoA  = self.__dLift_diAoA()
                dpJdpchi = self.__dpLift_dpchi()
            elif func == 'Drag':
                val      = self.__Drag()
                dfdiAoA  = self.__dDrag_diAoA()
                dpJdpchi = self.__dpDrag_dpchi()
            else:
                val = None
            self.__func_values[i]   = val
            self.__dfunc_diAoA[i,:] = dfdiAoA[:]
            self.__dpJ_dpchi[i,:]   = dpJdpchi[:]

        self.__display_info()
        self.set_computed(True)
                
    #-- Computation methods
    #-- Cl related methods
    def __Cl(self):
        Mach     = self.get_OC().get_Mach()
        localAoA = self.get_localAoA()
        airfoils = self.get_airfoils()
        Cl=0.0
        for i in xrange(self.__N):
            af = airfoils[i]
            Cl+=af.Cl(localAoA[i],Mach)*af.get_Sref()
        Cl/=self.get_Sref()
        return Cl
    
    def __dCl_diAoA(self):
        Mach     = self.get_OC().get_Mach()
        localAoA = self.get_localAoA()
        DlocalAoA_DiAoA = self.get_DlocalAoA_DiAoA()
        airfoils = self.get_airfoils()
        dCl_diAoA=zeros(self.__N)
        for i in range(self.__N):
            af = airfoils[i]
            dCl_diAoA+=af.ClAlpha(localAoA[i],Mach=Mach)*af.get_Sref()*DlocalAoA_DiAoA[i]
        dCl_diAoA/=self.get_Sref()
        
        return dCl_diAoA
    
    def __dpCl_dpchi(self):
        Mach     = self.get_OC().get_Mach()
        localAoA = self.get_localAoA()
        airfoils = self.get_airfoils()
        dlAoAdchi=self.get_DlocalAoA_Dchi()
        
        Cl=0.0
        dCl=zeros(self.__ndv)
        for i in xrange(self.__N):
            af=airfoils[i]
            Cl+=af.Cl(localAoA[i],Mach)*af.get_Sref()
            dCl+=af.ClAlpha(localAoA[i],Mach)*af.get_Sref()*dlAoAdchi[i,:] + af.dCl_dchi(localAoA[i],Mach)*af.get_Sref() + af.Cl(localAoA[i],Mach)*af.get_Sref_grad()
            
        dCldchi = (dCl*self.get_Sref() - Cl*self.get_Sref_grad())/(self.get_Sref()**2)        
        return dCldchi
    
    #-- Cd related methods
    def __Cd(self):
        Mach     = self.get_OC().get_Mach()
        airfoils = self.get_airfoils()
        localAoA = self.get_localAoA()
        iAoA     = self.get_iAoA()
        Cd=0.0 
        for i in xrange(self.__N):
            af      = airfoils[i]
            AoA     = localAoA[i]
            Cdloc=af.Cl(AoA,Mach)*sin(iAoA[i])+af.Cd(AoA,Mach)
            Cd+=Cdloc*af.get_Sref()
        Cd/=self.get_Sref()
        
        return Cd
    
    def __dCd_diAoA(self):
        Mach     = self.get_OC().get_Mach()
        airfoils = self.get_airfoils()
        localAoA = self.get_localAoA()
        iAoA     = self.get_iAoA()
        DlocalAoA_DiAoA = self.get_DlocalAoA_DiAoA()
        
        dCd_dAoA=zeros(self.__N)
        for i in range(self.__N):#Dependance by induced angles
            af=airfoils[i]
            AoA=localAoA[i]
            dCd_dAoA[i]=(af.ClAlpha(AoA,Mach)*sin(iAoA[i])+af.CdAlpha(AoA,Mach))*af.get_Sref()
 
        dCd_diAoA=dot(dCd_dAoA,DlocalAoA_DiAoA)
        
        for i in range(self.__N):#Dependance by projection of Cl : the induced drag.
            af=airfoils[i]
            dCd_diAoA[i]+=af.Cl(localAoA[i],Mach)*af.get_Sref()*cos(iAoA[i])
        dCd_diAoA/=self.get_Sref()
        
        return dCd_diAoA
    
    def __dpCd_dpchi(self):
        Mach     = self.get_OC().get_Mach()
        localAoA = self.get_localAoA()
        iAoA     = self.get_iAoA()
        airfoils = self.get_airfoils()
        dlAoAdchi=self.get_DlocalAoA_Dchi()
 
        Cd=0.0 
        dCd=zeros(self.__ndv)
        for i in range(self.__N):
            af=airfoils[i]
            AoA=localAoA[i]
            Cdloc=af.Cl(AoA,Mach)*sin(iAoA[i])+af.Cd(AoA,Mach)
            dCdloc=(af.ClAlpha(AoA,Mach)*sin(iAoA[i])+af.CdAlpha(AoA,Mach))*dlAoAdchi[i] + af.dCl_dchi(AoA,Mach)*sin(iAoA[i])+af.dCd_dchi(AoA,Mach)
            Cd+=Cdloc*af.get_Sref()
            dCd+=dCdloc*af.get_Sref()+Cdloc*af.get_Sref_grad()
        Cd/=self.get_Sref()
        dCddchi = (dCd*self.get_Sref()- Cd*self.get_Sref_grad())/(self.get_Sref()**2) 
         
        return dCddchi
    
    #-- Cm related methods (bugged for now)
    def __Cm(self):
        # Issue in moments calculation, no distances or sweep taken into account...
        print 'WARNING: Cm calculation to be checked...'
        Mach     = self.get_OC().get_Mach()
        airfoils = self.get_airfoils()
        localAoA = self.get_localAoA()
        Cm=0.0
        for i in xrange(self.__N):
            af=airfoils[i]
            Cm+=af.Cm(localAoA[i],Mach)*af.get_Sref()
        Cm/=self.get_Sref()
        return Cm
    
    def __dCm_diAoA(self):
        Mach     = self.get_OC().get_Mach()
        airfoils = self.get_airfoils()
        localAoA = self.get_localAoA()
        DlocalAoA_DiAoA = self.get_DlocalAoA_DiAoA()
        dCm=0.0
        for i in range(self.__N):
            af=airfoils[i]
            dCm+=af.CmAlpha(localAoA[i],Mach)*af.getSref()*DlocalAoA_DiAoA[i]
        dCm/=self.get_Sref()
        return dCm_diAoA
    
    def __dpCm_dpchi(self):
        Mach     = self.get_OC().get_Mach()
        localAoA = self.get_localAoA()
        airfoils = self.get_airfoils()
        dlAoAdchi=self.get_DlocalAoA_Dchi()
        
        Cm=0.0
        dCm=0.0
        for i in range(self.__N):
            af=airfoils[i]
            Cm+=af.Cm(localAoA[i],Mach)*af.get_Sref()
            dCm+=af.CmAlpha(localAoA[i],Mach)*af.get_Sref()*dlAoAchi[i]+af.dCm_dchi(localAoA[i],Mach)*af.get_Sref()+af.Cm(localAoA[i],Mach)*af.get_Sref_grad()
        Cm/=self.get_Sref()
        dCmdchi = (dCm*self.get_Sref()- Cm*self.get_Sref_grad())/(self.get_Sref()**2) 
        
        return dCmdchi
    
     #-- Lift related methods
    def __Lift(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        Cl = self.__Cl()
        Lift = Pdyn*Sref*Cl
        return Lift
    
    def __dLift_diAoA(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        dCl_diAoA=self.__dCl_diAoA()
        dLift_diAoA = Pdyn*Sref*dCl_diAoA
        return dLift_diAoA
    
    def __dpLift_dpchi(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        Sref_grad=self.get_Sref_grad()
        Cl = self.__Cl()
        dpCl_dpchi=self.__dpCl_dpchi()
        dpLift_dpchi = Pdyn*Sref*dpCl_dpchi+Pdyn*Sref_grad*Cl
        return dpLift_dpchi
        
    #-- Drag related methods
    def __Drag(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        Cd = self.__Cd()
        Drag = Pdyn*Sref*Cd
        return Drag
    
    def __dDrag_diAoA(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        dCd_diAoA = self.__dCd_diAoA()
        dDrag_diAoA = Pdyn*Sref*dCd_diAoA
        return dDrag_diAoA
    
    def __dpDrag_dpchi(self):
        Pdyn=self.get_OC().get_Pdyn()
        Sref=self.get_Sref()
        Sref_grad=self.get_Sref_grad()
        Cd=self.__Cd()
        dpCd_dpchi = self.__dpCd_dpchi()
        dpDrag_dpchi = Pdyn*Sref*dpCd_dpchi+Pdyn*Sref_grad*Cd
        return dpDrag_dpchi
    
    #-- Display methods
    def __display_info(self):
        print self.get_OC()
        print '\n*** aerodynamic functions and coefficients ***'
        for i, func in enumerate(self.__func_list):
            if func in ['Lift', 'Drag']:
                unit = '(N)'
            else:
                unit = ''
            print '  '+self.__func_list[i]+'\t=\t'+str(self.__func_values[i])+' '+unit 
