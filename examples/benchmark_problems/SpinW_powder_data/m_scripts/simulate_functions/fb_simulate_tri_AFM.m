function y = fb_simulate_IX_1D_test1(w,fitpars,msk)
% simulate loop to solve for the parameters 

fit_func = @tri_AFM_powder;
model_param = reshape(fitpars(1), 1, []);

Ei = 20; % meV
% Resolution for MARI with Gd chopper running at 200Hz and Ei=20meV (from PyChop)
eres = @(en) 2.1750e-04*sqrt((Ei-en).^3 .* ( (32.27217*(0.168+0.400*(Ei./(Ei-en)).^1.5)).^2 + (14.53577*(1.168+0.400*(Ei./(Ei-en)).^1.5)).^2) );
% Q-resolution (parameters for MARI)
e2k = @(en) sqrt( en .* (2*1.67492728e-27*1.60217653e-22) )./1.05457168e-34./1e10;
L1 = 11.8;  % Moderator to Sample distance in m
L2 = 4.0;   % Sample to detector distance in m
ws = 0.05;  % Width of sample in m
wm = 0.12;  % Width of moderator in m
wd = 0.025; % Width of detector in m
ki = e2k(Ei);
a1 = ws/L1; % Angular width of sample seen from moderator
a2 = wm/L1; % Angular width of moderator seen from sample
a3 = wd/L2; % Angular width of detector seen from sample
a4 = ws/L2; % Angular width of sample seen from detector
dQ = 2.35 * sqrt( (ki*a1)^2/12 + (ki*a2)^2/12 + (ki*a3)^2/12 + (ki*a4)^2/12 );

tri = sw_model('triAF',1);
fitpow = sw_fitpowder(tri, w, fit_func, model_param, 'independent');

% set parameters passed to powspec
fitpow.powspec_args.dE = eres; % energy resolution
fitpow.powspec_args.fastmode = true;
fitpow.powspec_args.neutron_output = true;
fitpow.powspec_args.nRand = 2e2; % low for speed (typically want > 1e3)
fitpow.powspec_args.hermit = true;
% set parameters passsed to sw_instrument
fitpow.sw_instrument_args = struct('dQ', dQ, 'ThetaMin', 3.5, 'Ei', Ei);

fitpow.powspec_args.dE = eres;
fitpow.powspec_args.fastmode = true;
fitpow.powspec_args.neutron_output = true;

[y, bg] = fitpow.calc_spinwave_spec(fitpars)
y = y'

end
