function [w, y, e, msk] = fb_wye_IX_1D_test7(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object
 
w = read_sqw(datafile);
addpath(genpath(path));

[y, e, msk] = sigvar_get(w);

msk(y==0) = 0;

y = y(msk);
e = sqrt(e(msk));

end

