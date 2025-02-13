function [fitpow, qmax_final, qmin_final] = process_tri_AFM(datafile, J1, qcens)
% Create fitpow and cut data based on qcens

dq = 0.05;
Ei = 20;
tri = sw_model('triAF', 1);
data = load(datafile).data;
fit_func =  @tri_AFM_powder;

fitpow = sw_fitpowder(tri, data, fit_func, [J1]);

eres = @(en) 2.1750e-04*sqrt((Ei-en).^3 .* ( (32.27217*(0.168+0.400*(Ei./(Ei-en)).^1.5)).^2 + (14.53577*(1.168+0.400*(Ei./(Ei-en)).^1.5)).^2) );
fitpow.crop_energy_range(1.5*eres(0), inf);
fitpow.crop_q_range(0.25, 3);

fitpow.nQ = 5;
fitpow.replace_2D_data_with_1D_cuts(qcens-dq, qcens+dq,'independent');

qmax_final = qcens + dq;
qmin_final = qcens - dq;

end
