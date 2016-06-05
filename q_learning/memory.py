from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np

class SimpleExperienceReplay(object):
    """
    Store up to `capacity` experiences for future lookup and training.

    Stored experiences will be sampled with a uniform distribution.
    """
    def __init__(self, capacity, batch_size, history_window, observation_shape):
        self.capacity = capacity
        self.batch_size = batch_size
        self.history_window = history_window
        self.index = 0
        self.size = 0

        obs_memory_shape = [capacity] + list(observation_shape)
        obs_batch_shape = [batch_size, history_window] + list(observation_shape)

        # memory
        self.obs = np.zeros(obs_memory_shape, dtype=np.uint8)
        self.actions = np.zeros(capacity, dtype=np.uint8)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.terminals = np.zeros(capacity, dtype=np.bool)

        # batch
        self.b_obs = np.zeros(obs_batch_shape, dtype=np.uint8)
        self.b_next_obs = np.zeros(obs_batch_shape, dtype=np.uint8)
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

    def sample(self):
        l = 0

        while l < self.batch_size:
            i = np.random.randint(self.history_window, self.size - self.history_window)

            # avoid sampling from disconnected episodes
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


class Buffer(object):
    """Rolling window of current state"""
    def __init__(self, history_window, observation_shape):
        self.size = history_window
        self._state = np.zeros([1, history_window] + list(observation_shape), dtype=np.uint8)

    def add(self, observation):
        """Shifts the observations to make room for the most recent one. 
        The most recent observation should be on the last index"""
        self._state[0, :self.size-1, ...] = self._state[0, 1:self.size, ...]
        self._state[0, self.size-1, ...] = observation

    def reset(self):
        self._state[...] = 0

    @property
    def state(self):
        return self._state




