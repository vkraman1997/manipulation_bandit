from bandits.bandit import Bandit
from distributions.betadistribution import BetaDistribution
import numpy as np
import copy
from scipy.stats import beta
from scipy.special import betainc
from scipy.special import beta
import matplotlib.pyplot as plt

class Influencelimiter_greedy():
    def __init__(self, bandit, agency, reward_reports, initial_reputation, track_reputation= True):
        self.bandit = bandit
        self.agency = agency
        self.posterior_history = {}
        self.prediction_history = {}
        self.reward_reports = reward_reports
        self.initial_reputation = initial_reputation
        self.track_reputation = track_reputation
        self.q_tilde = []
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
        self.q_tilde = []
        for (arm_index, arm) in enumerate(self.bandit.arms):
            self.prediction_history[arm_index]=[]
            self.posterior_history[arm_index] = [0.5]

            weight_0 = 1
            weight = copy.deepcopy(weight_0) #have to make dependant on initial reputation and 
            running_sum = 0.5 * weight

            #iterate through each agent and process their report
            for agent_index, agent in enumerate(self.agency.agents):
                # print(agent.id)
                gamma = min(self.agent_reputations[agent], 1)

                temp_running_sum = running_sum + (self.agency.agent_reports[agent][arm_index])
                temp_weight = weight + 1

                q_j = temp_running_sum / temp_weight
                self.prediction_history[arm_index].append(q_j)

                running_sum += self.agency.agent_reports[agent][arm_index] * gamma
                weight += gamma

                q_j_tilde = running_sum/weight
                self.posterior_history[arm_index].append(q_j_tilde)
    
            running_sum -= 0.5 * weight_0
            weight -= weight_0
            self.q_tilde.append(running_sum/weight)

    def select_arm(self, t, influence_limit = True):
        self._compute_IL_posterior(t)
        arm = np.argmax(self.q_tilde)
        return arm
        #we should also use quantile for the predictions!

    # def _update_reputations(self, arm, reward):
    #     # [print(dist.mean()) for dist in self.posterior_history[arm]]
    #     for index, agent in enumerate(self.agency.agents):
    #         gamma = min(1, self.agent_reputations[agent])
    #         q_tile_j_1 = self.posterior_history[arm][index]
    #         q_j = self.prediction_history[arm][index]
            
    #         self.agent_reputations[agent] += gamma * (self.scoring_rule(reward, q_tile_j_1) - self.scoring_rule(reward, q_j))
    #         if self.track_reputation == True:
    #             self.agent_reputations_track[agent].append(self.agent_reputations[agent])
    def _update_reputations(self, arm, reward):
        # [print(dist.mean()) for dist in self.posterior_history[arm]]
        # eta = np.sqrt((8 * np.log(len(self.agency.agents)))/self.bandit.T)
        eta = 1
        for index, agent in enumerate(self.agency.agents):
            # gamma = min(1, self.agent_reputations[agent])
            w = self.agent_reputations[agent]
            q_tile_j_1 = self.posterior_history[arm][index]
            q_j = self.prediction_history[arm][index]

            self.agent_reputations[agent] = w*np.exp(eta * (self.scoring_rule(reward, q_tile_j_1) - self.scoring_rule(reward, q_j)))

            # self.agent_reputations[agent] += gamma * (self.scoring_rule(reward, q_tile_j_1) - self.scoring_rule(reward, q_j))
            if self.track_reputation == True:
                self.agent_reputations_track[agent].append(self.agent_reputations[agent])

    # def _compute_T_posterior(self, selected_arm, reward):
    #     self.bandit.update(selected_arm, reward)

    def update(self, arm, reward):
        self._update_reputations(arm, reward)
        # self._compute_T_posterior(arm, reward)
    
    def plot_reputations(self):
        for (agent, reputations) in self.agent_reputations_track.items():
            plt.plot(reputations, label=agent.id)
        plt.legend()
        # plt.ylim([0, 1])
        plt.xlabel("Round (t)")
        plt.ylabel("Reputation")
        plt.show()

    def scoring_rule(self, r, q, rule = "quadratic"):
        if r == 1:
            return (1-q)**2
        else:
            return (q)**2

