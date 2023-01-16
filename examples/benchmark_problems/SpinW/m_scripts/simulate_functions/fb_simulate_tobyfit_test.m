function [spinw_y, e, msk] = fb_simulate_tobyfit_test(w)
amp=6000;    fwhh=0.2;
fitpars = [amp,fwhh];
cpars = {fitpars};

kk = tobyfit(w);
kk = kk.set_local_foreground;
kk = kk.set_fun(@testfunc_nb_sqw);
kk = kk.set_pin(cpars);
kk = kk.set_mc_points(2);
[wfit_1,fitpar_1] = kk.simulate();
[spinw_y, e, msk] = sigvar_get(wfit_1);
spinw_y(spinw_y < 1e-10) = 0;



