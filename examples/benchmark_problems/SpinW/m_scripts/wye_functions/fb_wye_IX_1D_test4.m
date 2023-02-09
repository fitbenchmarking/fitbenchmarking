function [w, y, e, msk] = fb_wye_IX_1D_test4(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

addpath(genpath(path));

% One-dimensional example
x1 = 1:100;

w = IX_dataset_1d (x1);

height = 1000; centre = 60; stdev = 10;
pf = [height, centre, stdev];       % parameters as needed by gauss

const = 10; df_by_dx1 = 0;
pb = [const, df_by_dx1];            % parameters for linear background

% Create dataset with 1d Gaussian on planar background as data
w = func_eval(w, @gauss, pf);           % 'foreground' model
w = w + func_eval(w, @linear_bg, pb);   % add 'background' model
win = noisify (w, 'poisson');           % noisify with poisson noise
w = win;

[spinw_y, spinw_e] = sigvar_get(w);

nslow = 100;  % each function evaluation of the 2D Gaussian will take
                % the same time as ~250,000 exponentiations
kk = multifit(w);
pf0 = [1100, 66, 13];   % starting parameters different from initial parameters
kk = kk.set_fun (@slow_func, {pf0, @gauss, nslow});
pb0 = [15,0];
kk = kk.set_bfun (@slow_func, {pb0, @linear_bg, nslow});
kk = kk.set_bfree ([1,0]);
[wfit, ffit] = kk.simulate();
[ ~, ~, msk] = sigvar_get(wfit);

y = spinw_y(msk);
e = spinw_e(msk);

end

