function [spinw_y, e, msk,fitpars] = fb_simulate_pcsmo_test(w,fitpars,msk)
%simulate loop to solve for the parameters 

persistent seed
if isempty (seed)
    rng(3,"twister");
    seed = rng();
else 
    rng(seed);
end

JF1 = -11.39; JA = 1.5; JF2 = -1.35; JF3 = 1.5; Jperp = 0.88; D = 0.074; en_width = 0.1;
frac = 1.e-6;
sw_obj = pcsmo(JF1, JA, JF2, JF3, Jperp, D);
%fitpars = [JF1 JA JF2 JF3 Jperp D en_width];

cpars = {fitpars 'mat', {'JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'}, ...
    'hermit', false, 'optmem', 0, 'useFast', false, 'formfact', ...
    true,'resfun', 'gauss', 'coordtrans', diag([2 2 1 1]), ...
    'use_brille', true, 'node_volume_fraction', frac, ...
    'use_vectors', false, 'Qtrans', diag([1./4 1./4 1.])};

tbf = tobyfit(w);
tbf = tbf.set_fun(@sw_obj.horace_sqw, {cpars{:}});
tbf = tbf.set_mc_points(5);
[fit_data , fit_pars] = tbf.simulate();

[spinw_y, e, ~] = sigvar_get(fit_data);

spinw_y=spinw_y(msk);