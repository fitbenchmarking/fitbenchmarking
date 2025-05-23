function y = tri_AFM_powder(x, p)

    y = @(x, p) matparser(x, 'param', p, 'mat', {'J_1'}, 'init', true);