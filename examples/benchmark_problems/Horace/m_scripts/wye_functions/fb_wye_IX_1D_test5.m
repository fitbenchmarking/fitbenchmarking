function [w, y, e, msk] = fb_wye_IX_1D_test5(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

addpath(genpath(path));

x1 = 50:70;
x2 = 1040:1060;

w = IX_dataset_2d (x1,x2);

height = 1000; centre = [60, 1050]; covmat = [10, 5, 20];
pf = [height, centre, covmat(:)'];     % parameters as needed by gauss2d

const = 10; df_by_dx1 = 0; df_by_dx2 = 0;
pb = [const, df_by_dx1, df_by_dx2];    % parameters for planar background

% Create dataset with 2d Gaussian on planar background as data
w = func_eval(w, @gauss2d, pf);         % 'foreground' model
w = w + func_eval(w, @linear2D_bg, pb);   % add 'background' model
win = noisify (w, 'poisson');        

w = win;
[y, e, msk] = sigvar_get(w);

msk(y==0) = 0;

y = y(msk);
e = sqrt(e(msk));
end

