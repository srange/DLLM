# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: iso-8859-1 -*-
# Copyright: Airbus

from DLLM.Controllers.Kernel.BaseController import BaseController
from numpy import zeros

class DesignVariable(BaseController):
    """
    PDesignVariable Class
    """
    CLASS_MSG = 'DesignVariable'
    ERROR_MSG = 'ERROR '+CLASS_MSG+'.'
    
    #--Constructor
    def __init__(self,PBCManager,Id,value,bounds):
        
        self.__bounds = None
        self.set_bounds(bounds)

        BaseController.__init__(self, PBCManager, Id, value=value, BCType='DesignVariable')
        
        self.__nvalue = 0.
        self.__norm_value()

    #--Private methods
    def __repr__(self):
        info_string=BaseController.__repr__(self)
        info_string+="\n   Value           :%24.16e"%self.get_value()
        info_string+="\n   LBounds         :%24s"%str(self.get_bounds())
        info_string+="\n   Gradient        : "+str(self.get_gradient())
        return info_string
    
    def __norm_value(self):
        lbnd=self.__bounds[0]
        ubnd=self.__bounds[1]
        self.__nvalue = (self.get_value() - lbnd) / ( ubnd - lbnd)
        
    def __revert_value(self):
        lbnd=self.__bounds[0]
        ubnd=self.__bounds[1]
        self.set_value(lbnd + self.__nvalue * (ubnd - lbnd))

    #--accessors
    def get_bounds(self):
        return self.__bounds
    
    def get_revert_fact(self):
        lbnd=self.__bounds[0]
        ubnd=self.__bounds[1]
        return (ubnd - lbnd)
    
    def get_normalized_value(self):
        return self.__nvalue

    #--setters
    def set_bounds(self, bounds):
        ERROR_MSG=self.ERROR_MSG+'set_bounds: '
        self.__bounds = bounds
        lbnd=self.__bounds[0]
        ubnd=self.__bounds[1]
        if lbnd >= ubnd:
            raise Exception,ERROR_MSG+' Lower bound greater or equal to upper bound!'
    
    def set_value(self,value,flag_updates=True, raise_error=False):
        """
        Set value of the PDesignVariable
        """
        BaseController.set_value(self,value,flag_updates=flag_updates)
        self.check_bounds(raise_error)
        self.__norm_value()
        
    def update_nomalized_value(self,nvalue):
        if self.get_normalized_value()!=nvalue:
            self.set_normalized_value(nvalue)
        
    def set_normalized_value(self,nvalue):
        self.__nvalue = nvalue
        self.__revert_value()

    #--methods
    def check_bounds(self, raise_error=False):
        """
        Check if variable is consistent
        """
        lbnd=self.__bounds[0]
        ubnd=self.__bounds[1]
        valid=True
        if self.get_value() < lbnd-1e-1:
            valid=False
            msg='WARNING: '+self.get_id()+' value=%24.16e'%self.get_value()+' is lower than lower boundary '+str(lbnd)+'.'
            print msg
            print 'Force value to lower bound'
            self.set_value(lbnd)
        if self.get_value() > ubnd+1e-1:
            valid=False
            msg='WARNING: '+self.get_id()+' value=%24.16e'%self.get_value()+' is greater than upper boundary '+str(ubnd)+'.'
            print msg
            print 'Force value to upper bound'
            self.set_value(ubnd)
        if not valid:
            if raise_error:
                print msg
                raise Exception,msg
            else:
                pass
                #print msg

    def handle_dv_changes(self):
        gradient=zeros(self.get_ndv())
        index=self.get_manager().get_dv_index(self.get_id())
        gradient[index]=1.
        self.set_gradient(gradient)
        
