function [w, y, e, msk] = fb_wye_IX_1D_test8(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object

w = read_sqw(datafile);
addpath(genpath(path));

[spinw_y, spinw_e, msk] = sigvar_get(w);

msk(spinw_y==0) = 0;

y = spinw_y(msk);
e = sqrt(spinw_e(msk));

end

