# -*-mode: python; py-indent-offset: 4; tab-width: 8; coding: iso-8859-1 -*-
#  DLLM (non-linear Differentiated Lifting Line Model, open source software)
# 
#  Copyright (C) 2013-2015 Airbus Group SAS
# 
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 
#  https://github.com/matthieu-meaux/DLLM.git
#
# @author : Matthieu MEAUX
#
from MDOTools.ValidGrad.FDValidGrad import FDValidGrad
from DLLM.DLLMGeom.wing_param import Wing_param
from DLLM.DLLMKernel.DLLMSolver import DLLMSolver
from MDOTools.OC.operating_condition import OperatingCondition
import numpy

OC=OperatingCondition('cond1')
OC.set_Mach(0.8)
OC.set_AoA(3.5)
OC.set_altitude(10000.)
OC.set_T0_deg(15.)
OC.set_P0(101325.)
OC.set_humidity(0.)
OC.compute_atmosphere()

wing_param=Wing_param('test_param',geom_type='Broken',n_sect=20)
wing_param.build_wing()
wing_param.set_value('span',34.1)
wing_param.set_value('sweep',34.)
wing_param.set_value('break_percent',33.)
wing_param.set_value('root_chord',6.1)
wing_param.set_value('break_chord',4.6)
wing_param.set_value('tip_chord',1.5)
wing_param.set_value('root_height',1.28)
wing_param.set_value('break_height',0.97)
wing_param.set_value('tip_height',0.33)
wing_param.convert_to_design_variable('span',(0.,50.))
wing_param.convert_to_design_variable('sweep',(0.,40.))
wing_param.convert_to_design_variable('break_percent',(20.,40.))
wing_param.convert_to_design_variable('root_chord',(5.,7.))
wing_param.convert_to_design_variable('break_chord',(3.,5.))
wing_param.convert_to_design_variable('tip_chord',(1.,2.))
wing_param.convert_to_design_variable('root_height',(1.,1.5))
wing_param.convert_to_design_variable('break_height',(0.8,1.2))
wing_param.convert_to_design_variable('tip_height',(0.2,0.5))
wing_param.build_linear_airfoil(OC, AoA0=-2., Cm0=-0.1, set_as_ref=True)
wing_param.build_airfoils_from_ref()
wing_param.update()

print wing_param



DLLM = DLLMSolver('Simple',wing_param,OC)
DLLM.run_direct()
iAoA0=DLLM.get_iAoA()
print 'iAoA0 shape',iAoA0.shape
print 'iAoA0=',iAoA0

def f(x):
    func=DLLM.comp_R(x)
    return func

def df(x):
    func_grad=DLLM.comp_dpR_dpiAoA(x)
    return func_grad

val_grad=FDValidGrad(2,f,df,fd_step=1.e-8)
ok,df_fd,df=val_grad.compare(iAoA0,treshold=1.e-6,return_all=True)


print '\n****************************************************'
if ok:
    print 'dpR_dpiAoA is valid.'
else:
    print '!!!! dpR_dpiAoA is NOT valid !!!!'
print '****************************************************'