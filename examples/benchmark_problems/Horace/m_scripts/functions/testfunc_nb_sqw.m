function weight = testfunc_nb_sqw (qh,qk,ql,en,pars)
% S(Q,w) for Nb phonons for purposes of testing Tobyfit only
%
%   >> weight = testfunc_nb_sqw (qh,qk,ql,en,pars)
%
%   qh, qk, ql, en   Arrays of Q and energy values at which to evaluate dispersion
%   pars            [Amplitude, fwhh]

ampl=pars(1);
sig=pars(2)/sqrt(log(256));

[wdisp,sf] = testfunc_nb_disp (qh,qk,ql,[]);
weight=(ampl/(sig*sqrt(2*pi)))*sf{1}.*exp(-(en-wdisp{1}).^2/(2*sig^2));
