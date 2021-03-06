from scipy.stats import beta
import numpy as np
from distributions.distribution import Distribution

class TruncatedNorm(Distribution):
    def __init__(self, mean= 0, std= 1):
        self.mean = mean
        self.std = 1 
    
    def mean(self):
        return (self.alpha)/ (self.alpha + self.beta)

    def variance(self):
         return beta.var(self.alpha, self.beta)

    def get_pdf(self, x):
        return beta.pdf(x, self.alpha, self.beta)
    
    def update(self, data):
        self.alpha += (data == 1)
        self.beta += (data == 0)
    
    def update_custom(self, delalpha, delbeta):
        self.alpha += delalpha
        self.beta += delbeta

    def sample(self):
        return np.asscalar(beta.rvs(self.alpha + 0.0001, self.beta + 0.0001, size=1))

    def sample_array(self, size):
        return beta.rvs(self.alpha + 0.0001, self.beta + 0.0001, size=size)

    def get_params(self):
        return self.alpha, self.beta
    
    def set_params(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def get_quantile(self, prob):
        return beta.ppf(prob, self.alpha + 0.0001, self.beta + 0.0001)