function [w, y, e, msk] = fb_wye_IX_1D_test3(datafile, path)
% Gets the w , x, y ,e and msk from the sqw object   

source_data = load(datafile);
addpath(genpath(path));
w = source_data.w3 ;
[y, e, msk] = sigvar_get(w);

msk(y==0) = 0;

y = y(msk);
e = sqrt(e(msk));

end

