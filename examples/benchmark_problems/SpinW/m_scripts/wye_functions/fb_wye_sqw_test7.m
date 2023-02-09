function [w, y, e, msk] = fb_wye_IX_1D_test7(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object
 
w = read_sqw(datafile);
addpath(genpath(path));

[spinw_y, spinw_e] = sigvar_get(w);

mss = multifit_sqw_sqw([w]);
mss = mss.set_fun(@sqw_bcc_hfm,  [5,5,0,10,0]);  % set foreground function(s)
mss = mss.set_free([1,1,0,0,0]); % set which parameters are floating
mss = mss.set_bfun(@sqw_bcc_hfm, {[5,5,1.2,10,0]}); % set background function(s)
mss = mss.set_bfree([1,1,1,1,1]);    % set which parameters are floating
mss = mss.set_bbind({1,[1,-1],1},{2,[2,-1],1});

% Simulate at the initial parameter values
[wfit_1, fitpar_1]  = mss.simulate();
[ ~, ~, msk] = sigvar_get(wfit_1);

y = spinw_y(msk);
e = spinw_e(msk);

end

