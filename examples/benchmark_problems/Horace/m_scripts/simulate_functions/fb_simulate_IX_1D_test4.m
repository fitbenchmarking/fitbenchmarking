function y = fb_simulate_IX_1D_test4(w,fitpars,msk)
% simulate loop to solve for the parameters 

pf0 = fitpars(1:3);
pb0 = [fitpars(4) 0];
nslow = 100;  % each function evaluation of the 2D Gaussian will take
                % the same time as ~250,000 exponentiations
kk = multifit(w);
kk = kk.set_fun (@slow_func_fb_test, {pf0, @gauss_fb_test, nslow});
kk = kk.set_bfun (@slow_func_fb_test, {pb0, @linear_bg_fb_test, nslow});
kk = kk.set_bfree ([1,0]);
[wfit, ffit] = kk.simulate();
[y, e] = sigvar_get(wfit);
y=y(msk);

end

