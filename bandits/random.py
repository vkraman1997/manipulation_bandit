from bandits.bandit import Bandit
import numpy as np
import random

class Random(Bandit):

    def select_arm(self, t, influence_limit= False):
        return random.randint(0, self.K-1)
        
    def update(self, arm, reward):
        self.arms[arm].pulls += 1
        self.arms[arm].rewards += reward



