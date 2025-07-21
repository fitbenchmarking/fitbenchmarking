function [w, y, e, msk] = fb_wye_spinw_2d(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).data;

msk = isnan(w.y);

%flat_y = w.y(:);
%clean_y = flat_y(~isnan(flat_y));
%flat_e = w.e(:);
%clean_e = flat_e(~isnan(flat_e));

%w.y = clean_y;
%w.e = clean_e;

w.y(isnan(w.y))=0;
w.e(isnan(w.e))=0;

y = vertcat(w.y);
e = vertcat(w.e);

end