function y=linear3D_bg(x1,x2,x3,p)
% Linear background function in three dimensiona
%
%   >> y = linear3D_bg (x1,x2,x3,p)
%
% Input:
% =======
%   x1  Array of x-axis values at which to evaluate function
%   x2  Array of second x-axis values at which to evaluate function
%   x3  Array of third x-axis values at which to evaluate function
%   p   Vector of parameters needed by the function:
%           y = p(1) + p(2)*x1 + p(3)*x2 + p(4)*x3
%
% Output:
% ========
%   y   Array of calculated y-axis values

if length(p)~=4
    error('Input parameters must be a vector of length 4');
end

y=p(1) + p(2).*x1 + p(3).*x2 + p(4).*x3;
