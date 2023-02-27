function y = slow_func (varargin)
% Evaluate a function but make it much slower
%
%   >> y = slow_func(x1,x2, ..., p, funchandle, nslow)
%
% Input:
% =======
%   x           Array of values at which to evaluate function
%
%   p           Vector of parameters needed by the function funchandle:
%               E.G. if a two dimensional Gaussian (see gauss)
%                   p = [height, centre, st_deviation]
%
%   funchandle  Handle to function to evaluate e.g. @gauss
%               The function can be any function that evaluates in
%               one dimension with the format expected by multifit
%
%   nslow       Number of times to run the time_waster function, which
%               alters each calculated value from the function call by a
%               factor <= 10^-13 (regardless of the value of nslow.
%               Each value of nslow takes about the time of 25
%               exponentiations per data point.
%                   nslow >=0
%
% Output:
% ========
%   y           Array of calculated y-axis values

[p, funchandle, nslow] = varargin{end-2:end};
y = funchandle (varargin{1:end-3}, p);
y = time_waster (y, nslow);
