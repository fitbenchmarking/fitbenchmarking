function [spinw_y, e, msk, fitpars] = fb_simulate_tobyfit_test(w,fitpars,msk)

cpars = {fitpars(1:2)};
bcpars = {fitpars(3:4)}
kk = tobyfit(w);
kk = kk.set_local_foreground;
kk = kk.set_fun(@testfunc_nb_sqw);
kk = kk.set_pin(cpars);
kk = kk.set_bfun(@testfunc_bkgd)
kk = kk.set_bpin(bcpars)
kk = kk.set_mc_points(2);
[wfit_1,fitpar_1] = kk.simulate();
[spinw_y, e] = sigvar_get(wfit_1);
spinw_y=spinw_y(msk==1);



