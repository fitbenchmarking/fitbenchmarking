function [w, y, e, msk] = fb_wye_tobyfit_test(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object


load(datafile, 'w1a', 'w1b');
addpath(genpath(path));
amp=6000;    fwhh=0.2;
fitpars = [amp,fwhh];
cpars = fitpars;
kk = tobyfit(w1a);
kk = kk.set_local_foreground;
kk = kk.set_fun(@testfunc_nb_sqw);
kk = kk.set_pin(cpars);
kk = kk.set_bfun(@testfunc_bkgd,[0,0]);
kk = kk.set_mc_points(5);
[wfit_1,fitpar_1] = kk.simulate();
[~,~,msk] = sigvar_get(wfit_1);
[spinw_y, spinw_e] = sigvar_get(w1a);

y = spinw_y(msk);
e = sqrt(spinw_e(msk));
w = w1a; 

end


