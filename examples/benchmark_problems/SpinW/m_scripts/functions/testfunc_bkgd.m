function y = testfunc_bkgd(x, p)
% Straight line
% 
%   >> y = mftest_bkgd(x,p)
%
% Input:
% =======
%   x   vector of x-axis values at which to evaluate function
%   p   vector or parameters needed by the function:
%           p = [const, grad]
%
% Output:
% ========
%   y       Vector of calculated y-axis values

% T.G.Perring

% Simply calculate function at input values
const=p(1);
grad=p(2);

y=const+x*grad;
