function [w, y, e, msk] = fb_wye_tobyfit_test(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object


load(datafile, 'w1a', 'w1b');
addpath(genpath(path));


[y, e, msk] = sigvar_get(w1a);

msk(y==0) = 0;

y = y(msk);
e = sqrt(e(msk));
w = w1a; 

end


