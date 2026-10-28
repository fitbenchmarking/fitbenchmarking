function [fitpow, qmax_final, qmin_final] = process_tri_AFM(datafile, params, qcens)
% Create fitpow and cut data based on qcens

dq = 0.05;
Ei = 20;
tri = sw_model('triAF', 1);
data = load(datafile).data;
fit_func =  @tri_AFM_powder;
J1 = params.J1;

fitpow = sw_fitpowder(tri, data, fit_func, [J1]);

fitpow.nQ = 5;
fitpow.replace_2D_data_with_1D_cuts(qcens-dq, qcens+dq,'independent');

qmax_final = qcens + dq;
qmin_final = qcens - dq;

end
