function [fitpow, qmax_final, qmin_final] = process_CrCl2Pym(datafile, params, qcens)
% Create fitpow and cut data based on qcens

J1 = params.J1
J2 = params.J2
J3 = params.J3
D1 = params.D1

CrPymCl2 = spinw;
CrPymCl2.genlattice('lat_const',[3.6688 12.103 7.0628],'angled',[90 94.236 90],'spgr','P 21/m')
CrPymCl2.addatom('r',[0 0 0],'S', 2,'label','Cr2','color','b')

% define interactions
%--------------------

CrPymCl2.gencoupling('maxDistance',7.5)
CrPymCl2.addmatrix('label','J1','value',J1,'color','red')
CrPymCl2.addmatrix('label','J2','value',J2,'color','green')
CrPymCl2.addmatrix('label','J3','value',J3,'color','pink')
CrPymCl2.addcoupling('mat','J1','bond',1)
CrPymCl2.addcoupling('mat','J2','bond',2)
CrPymCl2.addcoupling('mat','J3','bond',3)

vec = [1.82 0 -0.75];
v = [-1 0 0]; % starting axis vector - cannot be off axis, because then the matrix is incorrect
mag = dot(vec,vec)^0.5; %get magnitude for the end
vec = vec/mag; %normalise final unit vector
c = cross(v,vec); % cross product
e = c/(dot(c,c)^0.5); %normalised cross 
d = dot(v,vec); %dot product
si = dot(c,c)^0.5; %sin of the angle
K = [0 -1*e(3) e(2); e(3) 0 -1*e(1); -1*e(2) e(1) 0]; %'cross product matrix'

rot = diag([1 1 1])+si*K+(1-d)*K*K; %axis angle formula
ani=rot*diag(v)*inv(rot);

d_mat=ani.*-1;
CrPymCl2.addmatrix('value',d_mat.*D1,'label','D','color','r');
CrPymCl2.addaniso('D')

% optimise structure
%-------------------

CrPymCl2.genmagstr('mode','helical','k',[0.5 0.0 0.0],'n',[0 1 0 ], 'S',[1.8; 0; -0.7],'nExt',[2 1 1]);
CrPymCl2.optmagsteep('nRun', 500);

fit_func = @CrCl2Pym;
data = load(datafile).data;

fitpow = sw_fitpowder(CrPymCl2, data, fit_func, [J1,J2,J3,D1]);
dq = 0.025;
fitpow.replace_2D_data_with_1D_cuts(qcens-dq, qcens+dq,'independent');

qmax_final = qcens + dq;
qmin_final = qcens - dq;

end
