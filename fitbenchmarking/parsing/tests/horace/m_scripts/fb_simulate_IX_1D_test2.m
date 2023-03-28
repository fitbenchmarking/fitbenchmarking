function y = fb_simulate_IX_1D_test2(w,fitpars,msk)
% simulate loop to solve for the parameters 

forefunc = @mftest_gauss_bkgd;
mf = multifit(w);
mf = mf.set_fun(forefunc);
mf = mf.set_pin(fitpars);
[wout,fitpar] = mf.simulate();
[y, e] = sigvar_get(wout);
y=y(msk);

end

