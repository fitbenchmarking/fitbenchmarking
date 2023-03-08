function y = gauss3d (x1, x2, x3, p)
% Three-dimensional Gaussian
%
%   >> y = gauss3d (x1, x2, x3, p)
%
%  For each data point
%       y = h * exp(-1/2 * [dx1,dx2,dx3].*cov^-1.*[dx1;dx2;dx3])
%   where
%       dx1 = x1 - x1_0
%       dx2 = x2 - x2_0
%       dx3 = x3 - x3_0
%   
%       cov = Covariance matrix, a 3x3 matrix
%               (c11 is the variance of x1, c22 is the variance of x2
%               and c12/sqrt(c11*c22) is the correlation between x1 and x2).
%
% Input:
% =======
%   x1  Array of values at which to evaluate function along the first
%      dimension
%   x2  Array of values at which to evaluate function along the second
%      dimension. Must have the same size as x1
%   x3  Array of values at which to evaluate function along the third
%      dimension. Must have the same size as x1
%   p   Vector of parameters needed by the function:
%           p = [height, x1_0, x2_0, x3_0, c11, c12, c13, c22, c23, c33]
%
% Output:
% ========
%   y   Array of calculated y-axis values. Same size as x1.


if numel(p)~=10
    error('HERBERT:gauss:invalid_argument',...
        'The vector of parameters must have length 10')
end

ht=p(1); x1_0=p(2); x2_0=p(3); x3_0=p(4);
c11=p(5); c12=p(6); c13=p(7); c22=p(8); c23=p(9); c33=p(10);

m = inv([c11,c12,c13;c12,c22,c23;c13,c23,c33]);

dx1 = x1-x1_0;
dx2 = x2-x2_0;
dx3 = x3-x3_0;

y = ht*exp(-0.5*( m(1,1)*dx1.^2 + m(2,2)*dx2.^2 +m(3,3)*dx3.^2 +...
    2*m(1,2)*(dx1.*dx2) + 2*m(1,3)*(dx1.*dx3) + 2*m(2,3)*(dx2.*dx3)));
