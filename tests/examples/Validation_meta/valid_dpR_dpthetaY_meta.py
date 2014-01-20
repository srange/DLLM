from OpenDACE.ValidGrad.FDValidGrad import FDValidGrad
from DLLM.DLLMGeom.wing_param import Wing_param
from DLLM.DLLMKernel.DLLMSolver import DLLMSolver
from MDOTools.OC.operating_condition import OperatingCondition
import numpy

OC=OperatingCondition('cond1',atmospheric_model='simple')
OC.set_Mach(0.8)
OC.set_AoA(3.5)
OC.set_altitude(10000.)
OC.set_T0_deg(15.)
OC.set_P0(101325.)
OC.set_humidity(0.)
OC.compute_atmosphere()

wing_param=Wing_param('test_param',geom_type='Broken',n_sect=20)
wing_param.build_wing()
wing_param.set_value('test_param.span',34.1)
wing_param.set_value('test_param.sweep',34.)
wing_param.set_value('test_param.break_percent',33.)
wing_param.set_value('test_param.root_chord',6.1)
wing_param.set_value('test_param.break_chord',4.6)
wing_param.set_value('test_param.tip_chord',1.5)
wing_param.set_value('test_param.root_height',1.28)
wing_param.set_value('test_param.break_height',0.97)
wing_param.set_value('test_param.tip_height',0.33)
wing_param.convert_to_design_variable('test_param.span',10.,50.)
wing_param.convert_to_design_variable('test_param.sweep',0.,40.)
wing_param.convert_to_design_variable('test_param.break_percent',20.,40.)
wing_param.convert_to_design_variable('test_param.root_chord',5.,7.)
wing_param.convert_to_design_variable('test_param.break_chord',3.,5.)
wing_param.convert_to_design_variable('test_param.tip_chord',1.,2.)
wing_param.convert_to_design_variable('test_param.root_height',1.,1.5)
wing_param.convert_to_design_variable('test_param.break_height',0.8,1.2)
wing_param.convert_to_design_variable('test_param.tip_height',0.2,0.5)
wing_param.build_meta_airfoil(OC, '../MetaModelFixed.xml', relative_thickness=.12, camber=0., Sref=1., Lref=1., sweep=.0, set_as_ref=True)
wing_param.build_airfoils_from_ref()
wing_param.update()

print wing_param

thetaY0=wing_param.get_thetaY()
print 'thetaY0 shape',thetaY0.shape
print 'thetaY0=',thetaY0

DLLM = DLLMSolver(wing_param,OC)
DLLM.run_direct()
iAoA=DLLM.get_iAoA()

def f(x):
    wing_param.set_thetaY(x)
    func=DLLM.comp_R(iAoA)
    return func

def df(x):
    wing_param.set_thetaY(x)
    func_grad=DLLM.comp_dpR_dpthetaY()
    return func_grad

val_grad=FDValidGrad(2,f,df,fd_step=1.e-9)
ok,df_fd,df=val_grad.compare(thetaY0,treshold=1.e-6,return_all=True)


print '\n****************************************************'
if ok:
    print 'dpR_dpthetaY is valid.'
else:
    print '!!!! dpR_dpthetaY is NOT valid !!!!'
print '****************************************************'
