function [wdisp,sf] = testfunc_nb_disp (qh,qk,ql,par)
% Phonon dispersion relation for Nb acoustic phonons, from experiment
%
%   >> [wdisp,sf] = rbmnf3_disp (qh qk, ql, p)
%
% Input:
% ------
%   qh,qk,ql    Arrays of h,k,l
%   par         IX_dataset_1d object with points on the dispersion relation
%              along [00L] direction
%
% Output:
% -------
%   wdisp       Array of energies for the dispersion
%   sf          Array of spectral weights
%
% *** Spectral intensity, sf, is not correct

ql0 = [0, (4:25)/100];
w0 = [0, 1.1153    1.3390    1.5666    1.7740    1.9372    2.1364    2.3038...
    2.4585    2.5795    2.6848    2.8049    2.9320,...
    3.0588    3.1986    3.3549    3.5311    3.6665    3.8927    4.0382,...
    4.2400    4.4670    4.5901];

wdisp = interp1(ql0, w0, abs(ql), 'linear', 'extrap');
sf = ones(size(wdisp));

% Fudge until get correct intensity expression
sf=sf./wdisp;
sf(~isfinite(sf))=0;    % catch singularity at Bragg points if gap==0

% Standard output form:
wdisp = {wdisp};
sf = {sf};
