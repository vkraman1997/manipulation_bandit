from BetaDistribution import BetaDistribution
from BayesUCB import BayesUCB
from scipy.stats import bernoulli
from Random import Random
from Nature import Nature
import matplotlib.pyplot as plt
import numpy as np
from ThompsonSampling import ThompsonSampling 
from NonInfluenceLimiter import NonInfluenceLimiter
from NonInfluenceLimiter2 import NonInfluenceLimiter2
from NonInfluenceLimiter3 import NonInfluenceLimiter3
from InfluenceLimiter import InfluenceLimiter
from InfluenceLimiter2 import InfluenceLimiter2
from Oracle import Oracle
from Oracle2 import Oracle2
from Oracle3 import Oracle3
from Oracle4 import Oracle4
import scipy.stats
import copy

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a, 0), scipy.stats.sem(a, 0)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

T = 100
K = 5
num_exp = 10
num_reports = 10 #control noise
# trust = [False, True, False, False, True]
trust = [True, False, False, False, False] #1/3, #1/4?

world_priors = [BetaDistribution(1, 1) for k in range(K)]
nature = Nature(K, world_priors, len(trust))

bayes_ucb = BayesUCB(T, K, world_priors)
random = Random(T, K, world_priors)
thompson = ThompsonSampling(T, K, world_priors)

nil = NonInfluenceLimiter(copy.deepcopy(bayes_ucb), nature.agency, num_reports)
nil2 = NonInfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports)

il_rep_0 = InfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports, np.exp(0))
il_rep_1 = InfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports, np.exp(-1))
il_rep_2 = InfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports, np.exp(-1))
il_rep_5 = InfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports, np.exp(-5))
il_rep_10 = InfluenceLimiter2(copy.deepcopy(bayes_ucb), nature.agency, num_reports, 0)

oracle = Oracle4(copy.deepcopy(bayes_ucb), nature.agency)
oracle_test = Oracle4(copy.deepcopy(bayes_ucb), nature.agency)

# bandits = [bayes_ucb, il, nil2]
bandits = [il_rep_1, il_rep_10]

# key_map = {thompson: "thompson", bayes_ucb: "bayes_ucb", random: "random", nil: "nil", il: "il", nil2: "nil2", il2:"il2", nil3:"nil3"}
# key_color = {thompson: "red", bayes_ucb: "blue", random: "gray", nil: "green", il: "orange", nil2: "green", il2:"red", nil3:"green"}
key_map = {bayes_ucb: "bayes_ucb", il_rep_0: "il_rep_0", il_rep_1: "il_rep_1", il_rep_2: "il_rep_2", il_rep_5: "il_rep_5", il_rep_10:"il_rep_10", oracle_test:"oracle_test"}
key_color = {il_rep_0: "red", il_rep_1: "blue", il_rep_2: "green", il_rep_5: "yellow", il_rep_10:"purple", bayes_ucb:"orange", oracle_test:"green"}

cumulative_regret_history = {bandit: np.zeros((num_exp, T)) for bandit in bandits}
total_regret = {bandit: {exp:0 for exp in range(num_exp)} for bandit in bandits}

cumulative_trust_regret_history = {bandit: np.zeros((num_exp, T)) for bandit in bandits}
total_trust_regret = {bandit: {exp:0 for exp in range(num_exp)} for bandit in bandits}

#run bandit
for bandit in bandits:
    for exp in range(num_exp):
        #reset
        nature.initialize_arms()

        # np.random.shuffle(trust)
        nature.initialize_agents(trust, num_reports)
        
        bandit.reset()
        oracle.reset()
        # print(nature.hidden_params)
        # print("best arm:", nature.best_arm_mean)
        for t in range(T):
            # print(len(nature.agency.agents))
            # print("round", t)
            # nature.agency.track_reputations()
            reports = nature.get_agent_reports()
            arm = bandit.select_arm(t+1)

            # bandit.plot_posterior_history(nature.best_arm)
            # print("selected arm", arm)
            oracle_arm = oracle.select_arm(t+1)

            regret = nature.compute_per_round_regret(arm)
            # print("regret:", regret)
            oracle_regret = nature.compute_per_round_trust_regret(arm, oracle_arm)

            total_regret[bandit][exp] += regret
            cumulative_regret_history[bandit][exp][t] = total_regret[bandit][exp]/(t+1)

            total_trust_regret[bandit][exp] += oracle_regret
            cumulative_trust_regret_history[bandit][exp][t] = total_trust_regret[bandit][exp]/(t+1)

            reward = nature.generate_reward(arm)
            # print(reward)
            # print("reward:", reward)
            oracle_reward = nature.generate_reward(oracle_arm)

            bandit.update(arm, reward)
            oracle.update(oracle_arm, oracle_reward)

        # nature.agency.plot_reputations()
# average over experiments
average_cumulative_regret_history = {i:np.zeros(T) for i in bandits}
conf_cumulative_regret_history = {i:np.zeros(T) for i in bandits}
for (bandit, experiments) in cumulative_regret_history.items():
    mean, conf = mean_confidence_interval(experiments)
    average_cumulative_regret_history[bandit] = mean
    conf_cumulative_regret_history[bandit] = conf

average_cumulative_trust_regret_history = {i:np.zeros(T) for i in bandits}
conf_cumulative_trust_regret_history = {i:np.zeros(T) for i in bandits}
for (bandit, experiments) in cumulative_trust_regret_history.items():
    mean, conf = mean_confidence_interval(experiments)
    average_cumulative_trust_regret_history[bandit] = mean
    conf_cumulative_trust_regret_history[bandit] = conf

#plot
for (key, value) in average_cumulative_regret_history.items():
    plt.plot(average_cumulative_regret_history[key], label=key_map[key], color=key_color[key])
    h = conf_cumulative_regret_history[key]
    plt.fill_between(range(T), average_cumulative_regret_history[key] - h, average_cumulative_regret_history[key] + h,
                 color=key_color[key], alpha=0.2)

plt.legend()
plt.xlabel("Round (t)")
plt.ylabel("Mean Cumulative Regret")
plt.ylim(0, 1)
plt.show()

for (key, value) in average_cumulative_trust_regret_history.items():
    plt.plot(average_cumulative_trust_regret_history[key], label=key_map[key], color=key_color[key])
    h = conf_cumulative_trust_regret_history[key]
    plt.fill_between(range(T), average_cumulative_trust_regret_history[key] - h, average_cumulative_trust_regret_history[key] + h,
                 color=key_color[key], alpha=0.2)

plt.legend()
plt.xlabel("Round (t)")
plt.ylabel("Mean Cumulative Information Regret")
plt.ylim(0, 1)
plt.show()