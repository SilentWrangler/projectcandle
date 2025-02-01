import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import CnnPolicy, MlpPolicy

import gymnasium as gym
from collections import defaultdict
import numpy as np

from abc import ABC, abstractmethod

from players.models import Character

from ai.candle_ai_env import CandleAiEnvironment, create_observation
from ai.actions import AI_ACTIONS

from datetime import datetime

from tqdm import tqdm

class TestAgent:
    def __init__(
            self,
            env: gym.Env,
            learning_rate: float,
            initial_epsilon: float,
            epsilon_decay: float,
            final_epsilon: float,
            discount_factor: float = 0.95,
    ):
        """Initialize a Reinforcement Learning agent with an empty dictionary
        of state-action values (q_values), a learning rate and an epsilon.

        Args:
            env: The training environment
            learning_rate: The learning rate
            initial_epsilon: The initial epsilon value
            epsilon_decay: The decay for epsilon
            final_epsilon: The final epsilon value
            discount_factor: The discount factor for computing the Q-value
        """
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))

        self.lr = learning_rate
        self.discount_factor = discount_factor

        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon

        self.training_error = []

    def get_action(self, obs: tuple[int, int, bool]) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        # with probability epsilon return a random action to explore the environment
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return int(np.argmax(self.q_values[obs]))

    def update(
            self,
            obs: tuple[int, int, bool],
            action: int,
            reward: float,
            terminated: bool,
            next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""


        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        temporal_difference = (
                reward + self.discount_factor * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
                self.q_values[obs][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)

    def save_q_values(self, s, e):
        from pickle import dump
        import os

        save_path = "./pickled_models"
        timestring = datetime.now().strftime("%d-%m-%y_%H-%M")
        filename = os.path.join(save_path, f'Agent_s{s}_e{e}_{timestring}.pickle')


        with open(filename, mode='wb') as out:
            save = AgentSave(self.q_values,self.epsilon)
            dump(save, out)
        return filename

    def load_q_values(self, filename):
        from pickle import load
        with open(filename,mode='rb') as file:
            save = load(file)
            self.q_values = defaultdict(lambda: np.zeros(env.action_space.n), save.q_values )
            self.epsilon = save.epsilon


class AgentSave:
    def __init__(self,q_values,epsilon):
        self.q_values = dict(q_values)
        self.epsilon = epsilon



def train(steps: int = 50, n_episodes = 5):

    learning_rate = 0.01

    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2)  # reduce the exploration over time
    final_epsilon = 0.1

    env = gym.make("candle_ai_v0.1", steps)
    env = gym.wrappers.FlattenObservation(env)
    env = gym.wrappers.TimeLimit(env, steps)

    env = gym.wrappers.RecordEpisodeStatistics(env, n_episodes)

    agent = TestAgent(
        env = env,
        learning_rate=learning_rate,
        initial_epsilon=start_epsilon,
        epsilon_decay=epsilon_decay,
        final_epsilon=final_epsilon
    )

    print(f"{datetime.now()} Starting training on {str(env.metadata['name'])}.")

    for ep in tqdm(range(n_episodes)):
        try:
            o,i = env.reset()
            done = False

            for _ in tqdm(range(steps)):
                act = agent.get_action(tuple(o))
                n_o,rw,trm,trn,i = env.step(act)

                agent.update(
                    obs=tuple(o),
                    next_obs=tuple(n_o),
                    action=act,
                    reward=rw,
                    terminated=trm
                )

                done = trm or trn

                if done:
                    break

                o = n_o
            agent.decay_epsilon()
        except KeyboardInterrupt:
            print("Stopping...")
            break

    fname = agent.save_q_values(steps, n_episodes)
    print(f"Agent saved as {fname}")






class BaseActionAI(ABC):

    @abstractmethod
    def pick_action(self, character: Character) -> int:
        pass


class WeightedRandomAI(BaseActionAI):

    def __init__(self, *args, **kwargs):
        self.choices = []
        self.weights = []
        for action in AI_ACTIONS.ACTION_LIST:
            self.choices.append(AI_ACTIONS.__dict__[action])
            self.weights.append(kwargs.get(action.lower(),1))

    def pick_action(self, character: Character) -> int:
        from random import choices
        current_project = character.current_project
        if current_project is not None and current_project.work_required != 0:
            return AI_ACTIONS.DO_NOTHING
        return choices(self.choices, weights = self.weights)[0]


class TrainedActionAI(BaseActionAI):
    def __init__(self, *args, **kwargs):
        from pickle import load

        filename = kwargs['filename']

        with open(filename, mode='rb') as file:
            save = load(file)
            self.q_values = defaultdict(lambda: np.zeros(len(AI_ACTIONS.ACTION_LIST)), save.q_values)
            self.epsilon = save.epsilon


    def pick_action(self, character: Character) -> int:
        observation = create_observation(character, character.world)

        observation_hashable = tuple(observation.flatten())

        if np.random.random() < self.epsilon:
            return np.random.randint(0, len(AI_ACTIONS.ACTION_LIST))
        # with probability (1 - epsilon) act greedily (exploit)
        else:
            return int(np.argmax(self.q_values[observation_hashable]))


class DefaultTreeAI(BaseActionAI):

    RECRUITING_RANGE = 1
    RECRUITING_DRIVE = 5
    POP_SUPPORT_NEED = 5

    class SPECIALIZATIONS:
        ECONOMICS = (AI_ACTIONS.STUDY_ECONOMICS, 'economics')
        POLITICS = (AI_ACTIONS.STUDY_POLITICS, 'politics')
        MILITARY = (AI_ACTIONS.STUDY_MILITARY, 'military')
        SCIENCE = (AI_ACTIONS.STUDY_SCIENCE, 'science')

    def __init__(self, *args, **kwargs):
        self.specialization = kwargs['specialization']
        self.recruiting_range = kwargs.get('recruiting_range', DefaultTreeAI.RECRUITING_RANGE)
        self.recruiting_drive = kwargs.get('recruiting_range', DefaultTreeAI.RECRUITING_DRIVE)
        self.pop_support_need = kwargs.get('pop_support_need', DefaultTreeAI.POP_SUPPORT_NEED)
    def pick_action(self, character: Character) -> int:
        current_project = character.current_project
        if current_project is not None and current_project.work_required!=0:
            return AI_ACTIONS.DO_NOTHING
        if character.level(self.specialization[1])<1:
            return self.specialization[0]
        if self.specialization == DefaultTreeAI.SPECIALIZATIONS.POLITICS:
            if character.friends.count()<2:
                return AI_ACTIONS.MAKE_FRIEND
            if character.factions.count()<1:
                return AI_ACTIONS.MAKE_FACTION

            primary_faction_membership = character.factions.first()
            if primary_faction_membership.faction.members.count() < self.recruiting_drive:
                return AI_ACTIONS.INVITE_TO_FACTION
            if (primary_faction_membership.can_recruit
                    and primary_faction_membership.faction.pops.count() < self.pop_support_need):
                return AI_ACTIONS.GATHER_SUPPORT_FACTION

        if self.specialization == DefaultTreeAI.SPECIALIZATIONS.ECONOMICS:
            return AI_ACTIONS.BUILD_HOUSING



