function [w, y, e, msk] = fb_wye_spinw_2d(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).data;
msk = isnan(w.y);

y = vertcat(w.y);
e = vertcat(w.e);

end