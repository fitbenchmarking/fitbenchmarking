function [w, x ,y ,e] = fb_wxye_tobyfit_test()

s = 'C:\Users\vrs42921\Documents\CM\fitbenchmarking\examples\benchmark_problems\SpinW\data_files'
datafile = [s '/wdata1.mat']
load(datafile, 'w1a', 'w1b');
[spinw_y, spinw_e, msk] = sigvar_get(w1a);
y = spinw_y(:);
e = spinw_e(:);
w = w1a; 
bins = w1a.data.p;
a1  = bins{1};

for i = 1:length(a1) - 1
    a = a1(1,2:end) + a1(1,1:end-1);
end

x = reshape(a/2,[],1);


