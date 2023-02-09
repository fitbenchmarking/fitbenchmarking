function [wdisp,sf] = disp_bcc_hfm (qh,qk,ql,p)
% Spin wave dispersion relation for a Heisenberg ferromagnet with nearest
% neighbour exchange only.
%
%   >> [wdisp,sf] = disp_bcc_hfm (qh,qk,ql,js)
%
%   qh, qk, ql      Arrays of Q values at which to evaluate dispersion
%   p               parameters for dispersion relation: p=[gap,js]
%               gap     Empirical gap at magnetic zone centres
%               js      J*S in Hamiltonian in which each pair of spins is counted once only

gap=p(1);
js=p(2);
wdisp{1} = gap + (8*js)*(1-cos(pi*qh).*cos(pi*qk).*cos(pi*ql));
sf{1}=ones(size(qh));
