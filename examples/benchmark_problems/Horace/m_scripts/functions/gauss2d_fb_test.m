function y = gauss2d (x1, x2, p)
% Two-dimensional Gaussian
% 
%   >> y = gauss2d (x1, x2, p)
%
%  Function has form:
%       y = h * exp(-1/2 * [dx1,dx2].*cov^-1.*[dx1;dx2])
%   where
%       dx1 = x1 - x1_0
%       dx2 = x2 - x2_0
%   
%       cov = [c11, c12; c12, c22]  i.e. covariance matrix
%               (c11 is the variance of x1, c22 is the variance of x2
%               and c12/sqrt(c11*c22) is the correlation between x1 and x2).
%
% Input:
% =======
%   x1  Array of values at which to evaluate function along the first
%      dimension
%   x2  Array of values at which to evaluate function along the second
%      dimension. Must have the same size as x1
%   p   Vector of parameters needed by the function:
%           p = [height, x1_0, x2_0, c11, c12, c22]
%
% Output:
% ========
%   y   Vector of calculated y-axis values


if numel(p)~=6
    error('HERBERT:gauss2d:invalid_argument',...
        'The vector of parameters must have length 6')
end

ht=p(1); x1_0=p(2); x2_0=p(3);
c11=p(4); c12=p(5); c22=p(6);
det=c11*c22-c12^2;
m11=c22/det; m12=-c12/det; m22=c11/det;
dx1=x1-x1_0; dx2=x2-x2_0;
y=ht*exp(-0.5*(m11*dx1.^2 + 2*m12*(dx1.*dx2) + m22*dx2.^2));
