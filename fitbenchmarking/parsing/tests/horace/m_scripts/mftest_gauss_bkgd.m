function y = mftest_gauss_bkgd(x, p)
% Gaussian on linear background
% 
%   >> y = mftest_gauss_bkgd(x,p)
%
% Input:
% =======
%   x   vector of x-axis values at which to evaluate function
%   p   vector or parameters needed by the function:
%           p = [h1, c1, sig1, const, grad]
%
% Output:
% ========
%   y       Vector of calculated y-axis values

% T.G.Perring

% Simply calculate function at input values
ht=p(1);
cen=p(2);
sig=p(3);
const=p(4);
grad=p(5);

y=ht*exp(-0.5*((x-cen)/sig).^2) + (const+x*grad);
