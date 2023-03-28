function [y, name, pnames, pin] = gauss(x, p, flag)
% Gaussian function
%
%   >> y = gauss(x,p)
%   >> [y, name, pnames, pin] = gauss(x,p,flag)
%
% Input:
% =======
%   x   Vector of x-axis values at which to evaluate function
%   p   Vector of parameters needed by the function:
%           p = [height, centre, st_deviation]
%
% Optional:
%   flag    Alternative behaviour to follow other than function evaluation [optional]:
%           flag=1  (identify) returns just the function name and parameters
%           flag=2  (interactive guess) returns starting values for parameters
%
% Output:
% ========
%   y       Vector of calculated y-axis values
%
% if flag=1 or 2:
%   y       =[]
%   name    Name of function (used in mfit and possibly other fitting routines)
%   pnames  Parameter names
%   pin     iflag=1: = [];
%           iflag=2: = values of the parameters returned from interactive prompting


if numel(p)~=3
    error('HERBERT:gauss:invalid_argument',...
        'The vector of parameters must have length 3')
end

if nargin==2
    % Simply calculate function at input values
    y=p(1)*exp(-0.5*((x-p(2))/p(3)).^2);
else
    % Return parameter names or interactively prompt for parameter values
    y=[];
    name='Gaussian';
    pnames=char('Height','Centre','Sigma');
    if flag==1
        pin=zeros(size(p));
    elseif flag==2
        mf_msg('Click on peak maximum');
        [centre,height]=ginput(1);
        mf_msg('Click on half-height');
        [width,~]=ginput(1);
        sigma=0.8493218*abs(width-centre);
        pin=[height,centre,sigma];
    end
end

end
