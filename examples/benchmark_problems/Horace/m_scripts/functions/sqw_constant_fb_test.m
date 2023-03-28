function weight = sqw_constant (qh,qk,ql,en,p)
% Constant S(q,w)
% 
%   >> weight = sqw_bcc_hfm (qh,qk,ql,en,p)
%
% Input:
% =======
%   qh, qk, ql, en  Arrays of Q,w values at which to evaluate S(Q,w)
%   p               Single parameter giving the constant value of S(Q,w)
%
% Output:
% =======
%   weight          Spectral weight at (qh,qk,ql,en)

weight = p(1);
