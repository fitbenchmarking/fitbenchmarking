function [w, y, e, msk] = fb_wye_tri_AFM(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).w;
y = [w(1).y; w(2).y; w(3).y];
e = [w(1).e; w(2).e; w(3).e];
msk = []

end
