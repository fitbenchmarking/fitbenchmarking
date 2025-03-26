function [w, y, e, msk] = fb_wye_tri_AFM(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).data;
msk = [];

% remove all nan entries
NaN_rows_y = find(any(isnan(w.y),2));
w.y = w.y(sum(isnan(w.y),2)==0,:);
NaN_rows_e = find(any(isnan(w.e),2));
w.e = w.e(sum(isnan(w.e),2)==0,:);

w.x{2}([NaN_rows_y, NaN_rows_e]) = [];

y = vertcat(w.y);
e = vertcat(w.e);

end
