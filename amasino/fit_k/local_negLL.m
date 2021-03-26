%----- LOG-LIKELIHOOD FUNCTION
function sumerr = local_negLL(beta,choice,v1,d1,v2,d2)
    p = choice_prob(v1,d1,v2,d2,beta);

    % Trap log(0)
    ind = p == 1;
    p(ind) = 0.9999;
    ind = p == 0;
    p(ind) = 0.0001;
    % Log-likelihood
    err = (choice==1).*log(p) + (1 - (choice==1)).*log(1-p);
    % Sum of -log-likelihood
    sumerr = -sum(err);
end
