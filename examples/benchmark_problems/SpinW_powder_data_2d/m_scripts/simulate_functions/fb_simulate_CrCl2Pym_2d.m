function y = fb_simulate_tri_AFM_2d(w,fitpars,msk)
% simulate loop to solve for the parameters 

    CrPymCl2 = spinw;
    CrPymCl2.genlattice('lat_const',[3.6688 12.103 7.0628],'angled',[90 94.236 90],'spgr','P 21/m')
    CrPymCl2.addatom('r',[0 0 0],'S', 2,'label','Cr2','color','b')

    % define interactions
    %--------------------

    CrPymCl2.gencoupling('maxDistance',7.5)
    CrPymCl2.addmatrix('label','J1','value',fitpars(1),'color','red')
    CrPymCl2.addmatrix('label','J2','value',fitpars(2),'color','green')
    CrPymCl2.addmatrix('label','J3','value',fitpars(3),'color','pink')
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
    CrPymCl2.addmatrix('value',d_mat.*fitpars(4),'label','D','color','r');
    CrPymCl2.addaniso('D')

    % optimise structure
    %-------------------

    CrPymCl2.genmagstr('mode','helical','k',[0.5 0.0 0.0],'n',[0 1 0 ], 'S',[1.8; 0; -0.7],'nExt',[2 1 1]);
    CrPymCl2.optmagsteep('nRun', 500);

    %% instrument settings
    %--------------------

    Ei = 12.14; % meV

    % Resolution for LET (High Flux, 240/120Hz)
    eres = @(en) 1.2.* 2.4994e-04.*sqrt((Ei-en).^3 .* ( (33.44093.*(0.096+0.223.*(Ei./(Ei-en)).^1.5)).^2 + ...
                                    (29.15554.*(1.096+0.223.*(Ei./(Ei-en)).^1.5)).^2) );

    % Q-resolution (parameters for LET)
    e2k = @(en) sqrt( en .* (2*1.67492728e-27*1.60217653e-22) )./1.05457168e-34./1e10;
    L1 = 25;  % Moderator to Sample distance in m
    L2 = 3.5;   % Sample to detector distance in m
    ws = 0.05;  % Width of sample in m
    wm = 0.12;  % Width of moderator in m
    wd = 0.025; % Width of detector in m
    ki = e2k(Ei);
    a1 = ws/L1; % Angular width of sample seen from moderator
    a2 = wm/L1; % Angular width of moderator seen from sample
    a3 = wd/L2; % Angular width of detector seen from sample
    a4 = ws/L2; % Angular width of sample seen from detector
    dQ = 2.35 * sqrt( (ki*a1)^2/12 + (ki*a2)^2/12 + (ki*a3)^2/12 + (ki*a4)^2/12 );

    fit_func = @CrCl2Pym;
    model_params = reshape(fitpars(1:4), 1, []);

    fitpow = sw_fitpowder(CrPymCl2, w, fit_func, model_params);

    % set parameters passed to powspec
    fitpow.powspec_args.dE = eres; % emergy resolution
    fitpow.powspec_args.fastmode = false;
    fitpow.powspec_args.neutron_output = true;
    fitpow.powspec_args.nRand = 5e2;
    fitpow.powspec_args.hermit = false;
    % set parameters passsed to sw_instrument
    fitpow.sw_instrument_args = struct('dQ', dQ, 'ThetaMin', 3.5, 'Ei', Ei);

    [y, bg] = fitpow.calc_spinwave_spec(fitpars);
    y = y';
    y = y(~msk);

end