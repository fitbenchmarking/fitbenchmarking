function [w, y, e, msk] = fb_wye_tri_AFM(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).w;
y = vertcat(w.y);
e = vertcat(w.e);
msk = [];

end
