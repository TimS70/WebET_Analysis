%----- FIT DISCOUNTING MODEL - LOGISTIC FIT OF HYPERBOLIC DISCOUNTING
%     [info,p] = fit_discount_model(choice,v1,d1,v2,d2)
%
%     Fits a probabilistic discounting model to binary choices by maximum likelihood.
%
%     Calls local functions: log-likelihood, choice probability and discount
%
%     INPUTS
%     choice    - Dependent variable. The data should be *ungrouped*,
%                   such that CHOICE is a column of 0s and 1s, where 1 indicates 
%                   a choice of OPTION 2.
%     v1        - values of option 1 (ie, sooner option)
%     d1        - delays of option 1
%     v2        - values of option 2 (ie, later option)
%     d2        - delays of option 2
%
%     OUTPUTS
%     info      - data structure with following fields:
%                     .nobs      - number of observations
%                     .nb        - number of parameters
%                     .optimizer - function minimizer used
%                     .exitflag  - see FMINSEARCH
%                     .b         - fitted parameters; note that for all the
%                                  available models, the first element of B
%                                  is a noise term for the choice
%                                  function, the remaining elements are
%                                  parameters for the selected discount
%                                  functions. eg., for dfn='exp', B(2) is
%                                  the time constant of the exponential decay.
%                     .LL        - log-likelihood evaluated at maximum
%                     .LL0       - restricted (minimal model) log-likelihood
%                     .AIC       - Akaike's Information Criterion 
%                     .BIC       - Schwartz's Bayesian Information Criterion 
%                     .r2        - pseudo r-squared
%                   This is a struct array if multiple discount functions are fit.
%     p         - Estimated choice probabilities evaluated at the values & 
%                   delays specified by the inputs v1, v2, p1, p2. This is
%                   a cell array if multiple models are fit.
%

function [info,p] = fit_discount_model(choice,v1,d1,v2,d2)

    nobs = length(choice);
    alpha = 0.05;
    b0 = [.09 .008]; 
    %noise, kval starting points--can test different values if needed 
    
    % Fit model, attempting to use FMINUNC first, then falling back to FMINSEARCH
    if exist('fminunc','file')
       try
          optimizer = 'fminunc';
          OPTIONS = optimset('Display','off','LargeScale','off','MaxIter',1000);
          [b,negLL,exitflag,convg,g,H] = fminunc(@local_negLL,b0,OPTIONS,choice,v1,d1,v2,d2);
          if exitflag ~= 1 % trap occasional linesearch failures
             optimizer = 'fminsearch';
             fprintf('FMINUNC failed to converge, switching to FMINSEARCH\n');
          end         
       catch
          optimizer = 'fminsearch';
          fprintf('Problem using FMINUNC, switching to FMINSEARCH\n');
       end
    else
       optimizer = 'fminsearch';
    end

    if strcmp(optimizer,'fminsearch')
       optimizer = 'fminsearch';

       % https://de.mathworks.com/help/optim/ug/optimization-options-reference.html
       % 'TolCon',1e-6
       % 'DiffMinChange', 1e-4
       OPTIONS = optimset(...
            'Display','off', ...
            'TolFun', 1e-5, ...
            'TolX', 1e-5,...
            'Maxiter', 1000, ...
            'MaxFunEvals', 2000);
       [b,negLL,exitflag,convg] = fminsearch(@local_negLL,b0,OPTIONS,choice,v1,d1,v2,d2);
    end

    if exitflag ~= 1
       fprintf('Optimization FAILED, #iterations = %g\n',convg.iterations);
    else
       fprintf('Optimization CONVERGED, #iterations = %g\n',convg.iterations);
    end

    % Choice probabilities (for OPTION 2)
    p = choice_prob(v1,d1,v2,d2,b);
    % Unrestricted log-likelihood
    LL = -negLL;
    % Restricted log-likelihood
    LL0 = sum((choice==1).*log(0.5) + (1 - (choice==1)).*log(0.5));

    % Confidence interval, requires Hessian from FMINUNC
    try
        invH = inv(-H);
        se = sqrt(diag(-invH));
    catch
    end

    info.nobs = nobs;
    info.nb = length(b);
    info.optimizer = optimizer;
    info.exitflag = exitflag;
    info.b = b;

    try
        info.se = se;
        info.ci = [b-se*norminv(1-alpha/2) b+se*norminv(1-alpha/2)]; % Wald confidence
        info.tstat = b./se;
    catch
    end

    info.LL = LL;
    info.LL0 = LL0;
    info.AIC = -2*LL + 2*length(b);
    info.BIC = -2*LL + length(b)*log(nobs);
    info.r2 = 1 - LL/LL0;
end