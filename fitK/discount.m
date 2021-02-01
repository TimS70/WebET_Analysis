%----- DISCOUNT FUNCTION - HYPERBOLIC
%     y = discount(v,d,beta)
%
%     INPUTS
%     v     - values
%     d     - delays
%     beta  - discount rate
%
%     OUTPUTS
%     y     - discounted values
%
%     REVISION HISTORY:
%     brian lau 03.14.06 written
%     khoi 06.26.09 simplified 

function y = discount(v,d,beta)
    y = v./(1+beta(1).*d);
end