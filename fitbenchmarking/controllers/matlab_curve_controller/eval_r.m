function out=eval_r(x, y, varargin)
    global data_e;
    global cf;
    p = py.list(cell2mat(varargin));
    if length(data_e) == length(y)
        out = cf.eval_r(p);
    else
        x = py.numpy.array(x);
        y = py.numpy.array(y);
        e = py.numpy.ones_like(y);
        out = cf.eval_r(p, pyargs('x', x, 'y', y, 'e', e));
    end
end