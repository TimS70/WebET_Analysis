%----- CHOICE PROBABILITY FUNCTION - LOGIT
%     p = choice_prob(v1,d1,v2,d2,beta);
%
%     INPUTS
%     v1    - values of option 1 (ie, sooner option)
%     d1    - delays of option 1
%     v2    - values of option 2 (ie, later option)
%     d2    - delays of option 2
%     beta  - parameters, noise term (1) and discount rate (2)
%
%     OUTPUTS
%     p     - choice probabilities for the **OPTION 2**
%
%     REVISION HISTORY:
%     brian lau 03.14.06 written
%     khoi 06.26.09 simplified 

function [p,u1,u2] = choice_prob(v1,d1,v2,d2,beta)
    u1 = discount(v1,d1,beta(2:end));
    u2 = discount(v2,d2,beta(2:end));

    % logit, smaller beta = larger error
    p = 1 ./ (1 + exp(beta(1).*(u1-u2)));
end