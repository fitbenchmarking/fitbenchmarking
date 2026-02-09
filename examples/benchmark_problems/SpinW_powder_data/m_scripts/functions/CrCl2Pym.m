function y = CrCl2Pym(x, p)
    
    vec = [1.82 0 -0.75];
    v = [-1 0 0];
    d = dot(v,vec); %dot product
    c = cross(v,vec); % cross product
    e = c/(dot(c,c)^0.5); %normalised cross 
    K = [0 -1*e(3) e(2); e(3) 0 -1*e(1); -1*e(2) e(1) 0];
    si = dot(c,c)^0.5; %sin of the angle
    rot = diag([1 1 1])+si*K+(1-d)*K*K;
    ani=rot*diag(v)*inv(rot);
    d_mat=ani.*-1;
    selector = cat(3, eye(3), eye(3), eye(3), d_mat);
    fit_func =  @(x, p) matparser(x, 'param', p, 'mat', {'J1', 'J2', 'J3', 'D'}, 'selector', selector, 'init', true);