function [w, y, e, msk] = fb_wye_IX_1D_test3(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object   

source_data = load(datafile);
addpath(genpath(path));
w = source_data.w3 ;
[spinw_y, spinw_e] = sigvar_get(w);

pin=[100,50,7,0,0];
forefunc = @mftest_gauss_bkgd;
mf = multifit(w);
mf = mf.set_fun(forefunc);
mf = mf.set_pin (pin);
[wout,fitpar] = mf.simulate();
[ ~, ~, msk] = sigvar_get(wout);

y = spinw_y(msk);
e = spinw_e(msk);

end

