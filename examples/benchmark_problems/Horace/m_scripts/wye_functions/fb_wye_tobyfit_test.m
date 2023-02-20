function [w, y, e, msk] = fb_wye_tobyfit_test(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object


load(datafile, 'w1a', 'w1b');
addpath(genpath(path));


[spinw_y, spinw_e, msk] = sigvar_get(w1a);

msk(spinw_y==0) = 0;

y = spinw_y(msk);
e = sqrt(spinw_e(msk));
w = w1a; 

end


