function y = fb_simulate_IX_1D_test1(w,fitpars,msk)
% simulate loop to solve for the parameters 

forefunc = @mftest_gauss_bkgd_fb_test;
mf = multifit(w);
mf = mf.set_fun(forefunc);
mf = mf.set_pin(fitpars);
[wout,fitpar] = mf.simulate();
[y, e] = sigvar_get(wout);
y=y(msk);

end

