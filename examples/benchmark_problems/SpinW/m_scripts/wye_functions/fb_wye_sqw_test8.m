function [w, y, e, msk] = fb_wye_IX_1D_test8(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

w = read_sqw(datafile);
addpath(genpath(path));

[spinw_y, spinw_e] = sigvar_get(w);

mss = multifit_sqw(w);
mss = mss.set_fun(@sqw_bcc_hfm,  [5,5,1,10,0]);  % set foreground function(s)
mss = mss.set_free([0,1,1,1,1]); % set which parameters are floating
mss = mss.set_bfun(@linear_bkgd, [0,0]); % set background function(s)

% Simulate at the initial parameter values
[wfit_1, fitpar_1]  = mss.simulate();
[ ~, ~, msk] = sigvar_get(wfit_1);

y = spinw_y(msk);
e = spinw_e(msk);

end

