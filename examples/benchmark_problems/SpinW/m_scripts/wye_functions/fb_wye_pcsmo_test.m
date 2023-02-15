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

[spinw_y, spinw_e, msk] = sigvar_get(w1);

msk(spinw_y==0) = 0;

y = spinw_y(msk);
e = sqrt(spinw_e(msk));
w = w1; 
