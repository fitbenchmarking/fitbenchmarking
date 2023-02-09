function [spinw_y, e, msk, fitpars] = fb_simulate_sqw_test7(w,fitpars,msk)
%simulate loop to solve for the parameters 

cpars = [fitpars(1:2) 0 10 0];
bcpars = [fitpars(1:5)]
fitpars
mss = multifit_sqw_sqw([w]);
mss = mss.set_fun(@sqw_bcc_hfm); 
mss = mss.set_pin(cpars)                              % set foreground function(s)
mss = mss.set_free([1,1,0,0,0]); % set which parameters are floating
mss = mss.set_bfun(@sqw_bcc_hfm); % set background function(s)
mss = mss.set_bpin(bcpars)
mss = mss.set_bfree([1,1,1,1,1]);    % set which parameters are floating
mss = mss.set_bbind({1,[1,-1],1},{2,[2,-1],1});
[wfit_1, fitpar_1]  = mss.simulate();
[spinw_y, e] = sigvar_get(wfit_1);
spinw_y=spinw_y(msk==1);



