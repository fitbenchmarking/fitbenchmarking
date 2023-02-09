function [spinw_y, e, msk, fitpars] = fb_simulate_IX_1D_test4(w,fitpars,msk)
% simulate loop to solve for the parameters 

pf0 = fitpars(1:3);
pb0 = [fitpars(4) 0];
nslow = 100;  % each function evaluation of the 2D Gaussian will take
                % the same time as ~250,000 exponentiations
kk = multifit(w);
kk = kk.set_fun (@slow_func, {pf0, @gauss, nslow});
kk = kk.set_bfun (@slow_func, {pb0, @linear_bg, nslow});
kk = kk.set_bfree ([1,0]);
[wfit, ffit] = kk.simulate();
[spinw_y, e] = sigvar_get(wfit);
spinw_y=spinw_y(msk);

end

