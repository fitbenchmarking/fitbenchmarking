function weight = sqw_bcc_hfm_no_bkgd (qh,qk,ql,en,p)
% Wrapper function around dispersion relation to return spectral weight
%
%   >> weight = sqw_bcc_hfm_no_bkgd (qh,qk,ql,en,p)
%
% Input:
% =======
%   qh, qk, ql, en  Arrays of Q,w values at which to evaluate S(Q,w)
%
%   p               Parameters for S(Q,w) model: p=[scale,gap,js,gamma]
%               gap     Empirical gap at magnetic zone centres
%               js      J*S in Hamiltonian in which each pair of spins is counted once only
%               scale   Overall scaling factor
%               gamma   Inverse lifetime broadening applied as a Gaussian function
%
% Output:
% =======
%   weight          Spectral weight at (qh,qk,ql,en)

weight = p(3)*disp2sqw(qh,qk,ql,en,@disp_bcc_hfm,p(1:2),p(4));
