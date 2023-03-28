function y=linear2D_bg(x1,x2,p)
% Planar background function
%
%   >> y = linear2D_bg (x1,x2,p)
%
% Input:
% =======
%   x1  Array of x-axis values at which to evaluate function
%   x2  Array of second x-axis values at which to evaluate function
%   p   Vector of parameters needed by the function:
%           y = p(1) + p(2)*x1 + p(3)*x2
%
% Output:
% ========
%   y   Array of calculated y-axis values
%
%
% Synonymous with planar_bg

if length(p)~=3
    error('Input parameters must be a vector of length 3');
end

y=p(1) + p(2).*x1 + p(3).*x2;
