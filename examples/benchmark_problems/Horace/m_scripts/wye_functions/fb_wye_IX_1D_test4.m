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

[y, e, msk] = sigvar_get(w);

msk(y==0) = 0;

y = y(msk);
e = sqrt(e(msk));

end

