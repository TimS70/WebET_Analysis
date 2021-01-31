% Title: Solve for optimal parameters in hyperbolic discounting function
% (including simulated choices)
% Author: Alexander Fengler
% Date: February 7th 2015


% Provided a certain k for choices, this function return the k
% that minimizes errors for subjects that have preferences according to a
% logit destribution with unit variance

function [k, logLik] = fitK(data)

    function sumloglik = GenerateLogLik(cur_k)
        choiceProbabilities = GetPChoice(cur_k, ...
           data.aSS, data.aLL, data.tLL, data.choseLL);

        sumloglik = (-1)*(sum(log(choiceProbabilities)));
    end

    [k, logLik] = fminbnd(@GenerateLogLik,0,1);
end


