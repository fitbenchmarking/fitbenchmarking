.. _bayesian:

****************
Bayesian Fitting
****************

In Bayesian fitting, the aim is to estimate the posterior distributions of model parameters, using prior distributions which are refined using a likelihood function. 
Using Bayes Rule, for a dataset :math:`\boldsymbol{y}` and set of model parameters :math:`\boldsymbol{\theta}`, we have that:

.. math::
    p(\boldsymbol{\theta} | \boldsymbol{y}) = \frac{p(\boldsymbol{y} | \boldsymbol{\theta}) p(\boldsymbol{\theta})}{p(\boldsymbol{y})}.

Here, the term :math:`p(\boldsymbol{\theta} | \boldsymbol{y})` is the posterior distribution, representing the conditional probability of the model parameters given the data :math:`\boldsymbol{y}`.
The term :math:`p(\boldsymbol{y} | \boldsymbol{\theta})` is the conditional probability of the data given the model parameters :math:`\boldsymbol{\theta}`; this represents the likelihood function.
Finally, the term :math:`p(\boldsymbol{\theta})` is the prior distribution for the model parameters, representing the probability of particular model parameters existing.
The prior distribution describes a priori knowledge about the unknown model parameters. If there is no previous knowledge about the parameters, then the prior :math:`p(\boldsymbol{\theta}) = 1` can be used.
The denominator, :math:`p(\boldsymbol{y})`, is a normalization constant, which can be omitted in many cases, including those involving parameter estimation, as it does not depend on :math:`\boldsymbol{\theta}`.
Therefore, we can write Bayes' Theorem as

.. math::
    p(\boldsymbol{\theta} | \boldsymbol{y}) \propto p(\boldsymbol{y} | \boldsymbol{\theta}) p(\boldsymbol{\theta})

Assuming no previous knowledge about the model parameters, the posterior pdf can be approximated by the likelihood function (maximum likelihood estimate):

.. math::
    :label: likelihood

    p(\boldsymbol{\theta} | \boldsymbol{y}) \propto p(\boldsymbol{y} | \boldsymbol{\theta})

From here, further simplifications can be made by making assumptions related to the data. If it is assumed that the data are independent, their joint pdf can be written as the product of the probabilities for the individual measurements:

.. math::
    :label: independent_data

    p(\boldsymbol{\theta} | \boldsymbol{y}) = \prod_{i=1}^N p(y_i | \boldsymbol{\theta}).

In addition, if it is assumed that the noise associated with the measured data can be represented as a Gaussian process then

.. math::
    :label: Gaussian_process

    p(y_i | \boldsymbol{\theta}) = \frac{1}{\sigma_i \sqrt{2 \pi}} \text{exp} \left[ -\frac{(f(\theta, y_i) - y_i)^2}{2 \sigma_i^2} \right].

Equations :math:numref:`independent_data` and :math:numref:`Gaussian_process`, then allow the likelihood function (Equation :math:numref:`likelihood`) to be approximated by

.. math::
    p(\boldsymbol{y} | \boldsymbol{\theta}) \propto \text{exp} \left( -\frac{\chi^2}{2} \right)

Therefore, the logarithm of the posterior pdf is given by:

.. math::
    :label: loglike

    \text{log}_e \left[ p(\boldsymbol{\theta} | \boldsymbol{y} )\right] = - \frac{\chi^2}{2}.

More information on Bayesian methods is presented in the book Data Analysis - A Bayesian Tutorial, by D.S.Sivia.

.. _MCMC:

Markov Chain Monte Carlo Methods
********************************

Markov Chain Monte Carlo (MCMC) is a general method based on drawing values of :math:`\theta` from approximate distributions and then correcting those draws to better approximate the target posterior distribution, :math:`p(\theta|y)`.

A Markov Chain is a sequence of random variables :math:`\theta^1, \theta^2, ...,`` for which, at any t, the distribution of :math:`\theta^t` given all previous :math:`\theta`'s depends only on the most recent value (:math:`\theta^{t-1}`). 
In MCMC methods, the distribution of the sampled draws depends on the last value drawn, i.e. from a Markov Chain. At each step, the approximate distributions are improved, converging towards a target distribution.

Markov Chain simulation is used when it is not possible to sample directly from :math:`p(\theta|y)`, instead sampling iteratively in such a way that at each step of the process we expect to draw from a distribution that becomes closer to :math:`p(\theta|y)`.

**Metropolis-Hastings Algorithm**

1. Draw starting point :math:`\theta^0` (can be user specified or approximation based on data).
2. For :math:`t = 1,2,...,T` where T is chain size:
    a. Sample :math:`\theta^*` from a proposal distribution :math:`J_t(\theta^*|\theta^{t-1})`.
    b. Calculate the ratio of the target densities evaluated at :math:`\theta^*` and :math:`\theta^{t-1}`:
            
        .. math::
            r=\frac{p(\theta^*|y)/J_t(\theta^*|\theta^{t-1})}{p(\theta^{t-1}|y)/J_t(\theta^{t-1}|\theta^*)}
    c. Set

        .. math::
            \theta^t = \begin{cases}\theta^*, & \text{with probability}\ min(r,1) \\ \theta^{t-1}, & \text{otherwise} \end{cases}

Points to consider
******************
- MCMC methods do not have an explicit goal of refining the solution, so often a large chain size is required for convergence.
- It can take some time for the chain to converge to the target distribution and so it's common to exclue a number of initial samples
  from the output statistics. This early portion of the chain is referred to as the burn-in period.
- Rather than outputting fitted parameter values, MCMC methods output estimated posterior distributions for each model parameter which
  can be useful for calculating uncertainty estimates. Due to this, MCMC methods are not directly comparable to the other optimization algorithms
  implemented in Fitbenchmarking and therefore MCMC minimizers cannot be run with any other algorithm type. The method for assessing the accuracy of MCMC
  minimizers is outlined below.

  **Measuring Accuracy**

  1. Obtain 'true' parameter values using scipy curve fit and calculate :math:`2\sigma` errors.
  2. Taking the posterior distributions estimated using the MCMC method, for each model parameter integrate the area under the distribution between :math:`y-2\sigma` and :math:`y+2\sigma`
     where y is the 'true' parameter value. This integral gives the probability that the MCMC parameter estimate is within :math:`2\sigma` of the scipy fit.
  3. Take the product of the calculated probabilities (a probability should be calculated for each model parameter) to give an overall probability for all
     parameters being within the :math:`2\sigma` bounds.




