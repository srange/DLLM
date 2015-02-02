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
#  http://github.com/TBD
#
# Imports
from DLLM.DLLMGeom.wing_param import Wing_param
from DLLM.DLLMKernel.DLLMSolver import DLLMSolver
from MDOTools.OC.operating_condition import OperatingCondition
import numpy
import string

OC=OperatingCondition('cond1')
#OC.set_Mach(0.8)
#OC.set_Mach(0.6)
#OC.set_AoA(3.5)
AoA_list = [float(xx) for xx in range(0, 10)]
#Mach_list = [float(xx)/10. for xx in range(3, 9)]
Mach_list = [0.3]#,0.6,0.8]

OC.set_altitude(3000.)
OC.set_T0_deg(15.)
OC.set_P0(101325.)
OC.set_humidity(0.)

wing_param=Wing_param('test_param',geom_type='Broken',n_sect=20)
wing_param.build_wing()
wing_param.set_value('test_param.span',34.1)
wing_param.set_value('test_param.sweep',0.)
wing_param.set_value('test_param.break_percent',33.)
wing_param.set_value('test_param.root_chord',3.809036635014663)
wing_param.set_value('test_param.break_chord',3.809036635014663)
wing_param.set_value('test_param.tip_chord',3.809036635014663)
wing_param.set_value('test_param.root_height',0.8)
wing_param.set_value('test_param.break_height',0.8)
wing_param.set_value('test_param.tip_height',0.8)
wing_param.build_linear_airfoil(OC, AoA0=0., Cm0=-0.1, set_as_ref=True)
wing_param.build_airfoils_from_ref()
wing_param.update()
print 'AR=',wing_param.get_AR()
    
def RunPolar(wing_param, OC, AoA_list, polar_name):
    
    polar_name =polar_name + '_%.2E' % OC.get_Mach()+'.dat'
    set_polar_file(OC,  polar_name)
    
    for i,alpha in enumerate(AoA_list):
        OC.set_AoA(alpha)
        output, F_list_names = runDLLM(wing_param, OC)
        tags=['AoA']+F_list_names
        add_to_polar(polar_name, numpy.hstack([[alpha],output]), tags, i)
        
def runDLLM(wing_param, OC):
    
        DLLM = DLLMSolver('Rect',wing_param,OC)
        DLLM.run_direct()
        DLLM.run_post()
        
        output = DLLM.get_F_list()
        F_list_names = DLLM.get_F_list_names()
        return output, F_list_names      

def set_polar_file(OC, polar_name):
    
    with open(polar_name, 'w') as f:
	# Header is no up to date!!!
        header = '# polar for Mach ='+str(OC.get_Mach())
        f.write(header+'\n')
    f.closed
    
def add_to_polar(polar_name, values, tags, i):
    with open(polar_name, 'a') as f:
        if i == 0:
            line = "# "
            line+=string.join(tags,'\t')
            f.write(line+'\n')
        line  = ''
        for param in values:
            line = line+'%.10E    ' %  param 
        f.write(line+'\n')
    f.closed

for M in Mach_list:
    OC.set_Mach(M)
    OC.compute_atmosphere()
    RunPolar(wing_param,OC, AoA_list, 'RectSweep0')