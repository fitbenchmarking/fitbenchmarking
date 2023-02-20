function [w, y, e, msk] = fb_wye_IX_1D_test(datafile, path)
% Gets the w , y, e and msk from the sqw object

addpath(genpath(path));
source_data = load(datafile);
w = source_data.w1 ;

[spinw_y, spinw_e, msk] = sigvar_get(w);

msk(spinw_y==0) = 0;

y = spinw_y(msk);
e = sqrt(spinw_e(msk));

end

