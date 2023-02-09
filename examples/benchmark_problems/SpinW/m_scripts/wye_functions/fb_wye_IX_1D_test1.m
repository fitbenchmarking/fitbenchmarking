function [w, y, e, msk] = fb_wye_IX_1D_test(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

addpath(genpath(path));
source_data = load(datafile);
w = source_data.w1 ;

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

