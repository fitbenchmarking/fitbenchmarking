function [w, x ,y ,e,msk] = fb_wxye_tobyfit_test()

s = 'C:\Users\vrs42921\Documents\CM\fitbenchmarking\examples\benchmark_problems\SpinW\data_files'
datafile = [s '/wdata1.mat']
load(datafile, 'w1a', 'w1b');
amp=6000;    fwhh=0.2;
fitpars = [amp,fwhh];
cpars = {fitpars};

kk = tobyfit(w1a);
kk = kk.set_local_foreground;
kk = kk.set_fun(@testfunc_nb_sqw);
kk = kk.set_pin(cpars);
kk = kk.set_bfun(@testfunc_bkgd,[0,0]);
kk = kk.set_mc_points(2);
[wfit_1,fitpar_1] = kk.simulate();
[~,~,msk] = sigvar_get(wfit_1);
[spinw_y, spinw_e] = sigvar_get(w1a);

y = spinw_y(msk==1);
e = sqrt(spinw_e(msk==1));
w = w1a; 
bins = w1a.data.p;
a1  = bins{1}(msk==1);

for i = 1:length(a1) -1
    a = a1(1,2:end) + a1(1,1:end-1);
end

x = reshape(a/2,[],1);


