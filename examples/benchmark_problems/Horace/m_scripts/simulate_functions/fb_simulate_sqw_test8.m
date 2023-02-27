function y = fb_simulate_sqw_test8(w,fitpars,msk)
%simulate loop to solve for the parameters 

cpars = [5 fitpars(1:4)];
bcpars = fitpars(5:6)
mss = multifit_sqw(w);
mss = mss.set_fun(@sqw_bcc_hfm_fb_test);  % set foreground function(s)
mss = mss.set_pin(cpars)
mss = mss.set_free([0,1,1,1,1]); % set which parameters are floating
mss = mss.set_bfun(@linear_bkgd_fb_test); % set background function(s)
mss = mss.set_bpin(bcpars)
[wfit_1, fitpar_1]  = mss.simulate();
[y, e] = sigvar_get(wfit_1);
y=y(msk);



