from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np

class SimpleExperienceReplay(object):

    def __init__(self, capacity, batch_size, history_window, height, width):
        self.capacity = capacity
        self.batch_size = batch_size
        self.history_window = history_window
        self.index = 0
        self.size = 0

        obs_memory_shape = (capacity, height, width)
        obs_buffer_shape = (batch_size, history_window, height, width)

        # memory
        self.obs = np.zeros(obs_memory_shape, dtype=np.float32)
        self.actions = np.zeros(capacity, dtype=np.uint8)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.terminals = np.zeros(capacity, dtype=np.bool)

        # buffer
        self.b_obs = np.zeros(obs_buffer_shape, dtype=np.float32)
        self.b_next_obs = np.zeros(obs_buffer_shape, dtype=np.float32)
        self.b_actions = np.zeros(batch_size, dtype=np.uint8)
        self.b_rewards = np.zeros(batch_size, dtype=np.float32)
        self.b_terminals = np.zeros(batch_size, dtype=np.bool)


    def add(self, experience):
        obs, action, reward, terminal = experience

        self.obs[self.index, ...] = obs
        self.actions[self.index] = action
        self.rewards[self.index] = reward
        self.terminals[self.index] = terminal

        self.index = (self.index + 1) % self.capacity
        self.size = min(self.capacity, self.size + 1)

    # def last_history(self, current_obs):
    #     prev = self.obs[i-self.history_window-1:i, ...]
    #     return np.

    def sample(self):
        l = 0

        while l < self.batch_size:
            i = np.random.randint(self.history_window, self.size - self.history_window)

            # only sample from past observations
            if i - self.history_window >= self.index and self.index <= i:
                continue

            # avoid frames from different episodes
            if self.terminals[i-self.history_window:i].any():
                continue

            self.b_obs[l, ...] =  self.obs[i-self.history_window:i, ...]
            self.b_next_obs[l, ...] =  self.obs[i:i+self.history_window, ...]
            self.b_actions[l] = self.actions[i]
            self.b_rewards[l] =  self.rewards[i]
            self.b_terminals[l] = self.terminals[i]

            l += 1


        return (self.b_obs, self.b_actions, self.b_rewards, self.b_next_obs, self.b_terminals)

    def reset(self):
        self.obs[...] = 0
        self.actions[...] = 0
        self.rewards[...] = 0
        self.terminals[...] = 0
        self.b_obs[...] = 0
        self.b_next_obs[...] = 0
        self.b_actions[...] = 0
        self.b_rewards[...] = 0
        self.b_terminals[...] = 0

