function [x, fval, exitflag] = fb_fminsearch(fun, x0)
    % fun is an int

    % Create an anonymous function to allow interface to MEX file
    % The MEX file will call the associated function.
    fun_wrapper = @(x) evalfunction(fun, x);
    
    [x, fval, exitflag] = fminsearch(fun_wrapper, x0);
    exitflag = typecast(exitflag, 'int32');
end
