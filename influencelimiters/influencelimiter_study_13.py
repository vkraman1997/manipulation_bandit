from bandits.bandit import Bandit
from distributions.betadistribution import BetaDistribution
import numpy as np
import copy
from scipy.stats import beta
from scipy.special import betainc
from scipy.special import beta
import matplotlib.pyplot as plt

class InfluenceLimiter_study_13():
    def __init__(self, bandit, agency, reward_reports, initial_reputation, track_reputation= True):
        self.bandit = bandit
        self.agency = agency
        self.posterior_history = {}
        self.prediction_history = {}
        self.reward_reports = reward_reports
        self.initial_reputation = initial_reputation
        self.track_reputation = track_reputation
        super().__init__()
    
    def reset(self):
        self.bandit.reset()
        self.posterior_history = {}
        self.prediction_history = {}
        self.__initialize_reputations()

    def __initialize_reputations(self):
        self.agent_reputations = {agent:self.initial_reputation for agent in self.agency.agents}
        # self.agent_reputations = [int(agent.trustworthy == True) for agent in self.agency.agents]
        if self.track_reputation:
            self.agent_reputations_track = {agent:[self.initial_reputation] for agent in self.agency.agents}

    def plot_posterior_history(self, arm):
        x = np.linspace(0, 1.0, 100)
        for (index, dist) in enumerate(self.prediction_history[arm]):
            a, b = dist.get_params()
            y = beta.pdf(x, a, b)
            plt.plot(x, y, label=index)
        plt.legend()
        plt.show()

    def _compute_SMA(self, arm_index):
        npa = np.asarray(copy.deepcopy(self.agency.agent_reports))
        return np.mean(npa[:,arm_index])
    
    def _compute_IL_posterior(self, t):
        for (arm_index, arm) in enumerate(self.bandit.arms):
            pre_alpha, pre_beta = copy.deepcopy(arm.reward_dist.get_params())
            prediction_weighted_sum = 0
            weight_sum = 0
            reports = 0

            #iterate through each agent and process their report
            for agent_index, agent in enumerate(self.agency.agents):
                w = min(self.agent_reputations[agent], 1)
                weight_sum += w
                reports += agent.num_reports * w
                prediction_weighted_sum += w * self.agency.agent_reports[agent][arm_index]
               
    
            y_tilde_alpha = (prediction_weighted_sum/weight_sum) * (reports)
            y_tilde_beta = (1-(prediction_weighted_sum/weight_sum)) * (reports)
            arm.influence_reward_dist.set_params(y_tilde_alpha + pre_alpha, y_tilde_beta + pre_beta)

    def select_arm(self, t, influence_limit = True):
        self._compute_IL_posterior(t)
        return self.bandit.select_arm(t, influence_limit = influence_limit)
        #we should also use quantile for the predictions!

    def _update_reputations(self, arm, reward):
        # eta = np.sqrt((8 * np.log(len(self.agency.agents)))/self.bandit.T)
        for index, agent in enumerate(self.agency.agents):
            w = min(self.agent_reputations[agent], 1)
            self.agent_reputations[agent] += w*(self.scoring_rule(reward, 0.5) - self.scoring_rule(reward, self.agency.agent_reports[agent][arm]))
            if self.track_reputation == True:
                self.agent_reputations_track[agent].append(self.agent_reputations[agent])

    def _compute_T_posterior(self, selected_arm, reward):
        self.bandit.arms[selected_arm].reward_dist.update(reward)

    def update(self, arm, reward):
        self._update_reputations(arm, reward)
        self._compute_T_posterior(arm, reward)
    
    def plot_reputations(self):
        for (agent, reputations) in self.agent_reputations_track.items():
            plt.plot(reputations, label=agent.id)
        plt.legend()
        plt.xlabel("Round (t)")
        plt.ylim([0, 1])
        plt.ylabel("Reputation")
        plt.show()

    def scoring_rule(self, r, q, rule = "quadratic"):
        if r == 1:
            return (1-q)**2
        else:
            return (q)**2

