function [w, y, e, msk] = fb_wye_pcsmo_test(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

sqw_file = datafile
addpath(genpath(path));

ne = 10;
frac = 1.e-6;
ei = [25, 35, 50, 70, 100, 140];
freq = [300, 200, 200, 250, 300, 400];
proj = ortho_proj([1, 0, 0], [0, 1, 0], 'type', 'rrr');

sample = IX_sample(true,[0,0,1],[0,1,0],'cuboid',[0.01,0.05,0.01]);
sample.angdeg = [90 90 90];
sample.alatt = [3.4 3.4 3.4];
maps = maps_instrument(ei(4), freq(4), 'S');
lower_e = ei(4)*0.2; upper_e = ei(4)*0.7;
ebin = [lower_e, ei(4)/25, upper_e];
w1 = cut_sqw(sqw_file, proj, [-1, 2/39, 1], [-1, 2/39, 1], [-10, 10], ebin);
w1 = set_sample(w1,sample);
w1 = set_instrument(w1,maps);
w1 = mask_random_fraction_pixels(w1, 0.00001);

JF1 = -11.39; JA = 1.5; JF2 = -1.35; JF3 = 1.5; Jperp = 0.88; D = 0.074; en_width = 0.1;
fitpars = [JF1 JA JF2 JF3 Jperp D en_width];
sw_obj = pcsmo(JF1, JA, JF2, JF3, Jperp, D);
cpars = {fitpars 'mat', {'JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)'}, ...
    'hermit', false, 'optmem', 0, 'useFast', false, 'formfact', ...
    true,'resfun', 'gauss', 'coordtrans', diag([2 2 1 1]), ...
    'use_brille', true, 'node_volume_fraction', frac, ...
    'use_vectors', false, 'Qtrans', diag([1./4 1./4 1.])};

tbf = tobyfit(w1);
tbf = tbf.set_fun(@sw_obj.horace_sqw, {cpars{:}});
tbf = tbf.set_mc_points(5);
[w_fit , fit_pars] = tbf.simulate();
[~, ~, msk] = sigvar_get(w_fit);
[spinw_y, spinw_e, ~] = sigvar_get(w1);
y = spinw_y(msk);
e = sqrt(spinw_e(msk));
w = w1; 
