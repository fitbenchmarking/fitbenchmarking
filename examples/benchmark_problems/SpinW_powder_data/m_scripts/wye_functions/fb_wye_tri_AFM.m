function [w, y, e, msk] = fb_wye_tri_AFM(datafile, path)
% Gets w , x, y ,e and msk from the object

w = load(datafile).data;
y = vertcat(w.y);
e = vertcat(w.e);
msk = [];

% remove all NaN entries
NaN_cols_y = find(any(isnan(y)));
y = y(:,sum(isnan(y),1)==0)
NaN_cols_e = find(any(isnan(e)));
e = e(:,sum(isnan(e),1)==0)

for i=1:size(y,1)
    w(i).y = y(i,:);
    w(i).e = e(i,:);
    w(i).x([NaN_cols_y, NaN_cols_e]) = [];
end
