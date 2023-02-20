function weight = sqw_bcc_hfm_fb_test (qh,qk,ql,en,p)
% Wrapper function around dispersion relation to return spectral weight
%
%   >> weight = sqw_bcc_hfm (qh,qk,ql,en,p)
%
% Input:
% =======
%   qh, qk, ql, en  Arrays of Q,w values at which to evaluate S(Q,w)
%
%   p               Parameters for S(Q,w) model: p=[scale,gap,js,gamma,bkconst]
%               gap     Empirical gap at magnetic zone centres
%               js      J*S in Hamiltonian in which each pair of spins is counted once only
%               scale   Overall scaling factor
%               gamma   Inverse lifetime broadening applied as a Gaussian function
%               bkconst Background constant
%
% Output:
% =======
%   weight          Spectral weight at (qh,qk,ql,en)

weight = p(3)*disp2sqw(qh,qk,ql,en,@disp_bcc_hfm_fb_test,p(1:2),p(4)) + p(5);
