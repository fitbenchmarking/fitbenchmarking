function yout=spinw_mnf2_fit(Q,E,pars,ok,Ei,dE,dQ,s)

S=5/2;
scalefac = pars(1);
J=pars(2:3);
D=pars(4);
bg=pars(5);

% Setup spinw model
mnf2 = spinw;
mnf2.genlattice('lat_const', [4.87 4.87 3.31], 'angle', [90 90 90]*pi/180, 'sym', 'P 42/m n m');
mnf2.addatom('r', [0 0 0], 'S', S, 'label', 'MMn2', 'color', 'b')
mnf2.gencoupling('maxDistance', 5)
mnf2.addmatrix('label', 'J1', 'value', J(1), 'color', 'red');
mnf2.addmatrix('label', 'J2', 'value', J(2), 'color', 'green');
mnf2.addcoupling('mat', 'J1', 'bond', 1)
mnf2.addcoupling('mat', 'J2', 'bond', 2)
mnf2.addmatrix('label', 'D', 'value', diag([0 0 D]), 'color', 'black');
mnf2.addaniso('D')
mnf2.genmagstr('mode', 'direct', 'S', [0 0; 0 0; 1 -1])

try
    % Powder average spin waves:
    mnf2powspec=mnf2.powspec_ran(unique(Q)','Evect',unique(E)',...
        'binType','cbin','nRand',400,'hermit',true,...
        'formfact',true,'s_rng',s);%note that you can change the number of random Q points
    %A smaller number gives a noisier output, but faster evaluation.

    %Give a file containing Nx2 matrix giving Etrans and dE. From Pychop for Ei=11meV 240/120Hz
    mnf2powspec = sw_instrument(mnf2powspec,'dE',dE,...
        'Ei',Ei,'dQ',dQ);

    yout=abs(scalefac).*mnf2powspec.swConv';
    yout=yout+bg;
    
    yout=yout(ok);
    
    %Can be odd cases when small number of additional points come from sim
    %as NaN. In this case replace them with bg:
    f=isnan(yout);
    yout(f)=bg;
    
catch
    %deal with the case that spinwave calc failed - e.g. exchanges
    %inconsistent with known magnetic structure. Returns a signal array
    %that is so massive that it will ensure the fitting algorithm avoids
    %such places
    yout=ones(numel(Q.signal),numel(Q.error)).*1e12;
    yout=yout(ok);
end