function y=linear_bg(x,p)
% Linear background function
%
%   >> y = linear_bg (x,p)
%
% Input:
% =======
%   x   Array of x-axis values at which to evaluate function
%   p   Vector of parameters needed by the function:
%           y = p(1) + p(2)*x
%
% Output:
% ========
%   y   Array of calculated y-axis values


if length(p)~=2
    error('Input parameters must be a vector of length 2');
end

y=p(1) + p(2).*x;
