import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import CnnPolicy, MlpPolicy

from ai.candle_ai_env import CandleAiEnvironment

def train(steps: int = 1_000):
    env = CandleAiEnvironment()

    #exitenv = ss.black_death_v3(env)

    env.reset()

    print(f"Starting training on {str(env.metadata['name'])}.")

    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, 8, num_cpus=1, base_class="stable_baselines3")

    model = PPO(
        MlpPolicy,
        env,
        verbose=3,
        batch_size=256,
    )

    model.learn(total_timesteps = steps)

    model.save(f"{env.unwrapped.metadata.get('name')}_world_{env.unwrapped.wid}")

    print("Model has been saved.")

    env.close()


def eval(num_games: int = 100):
    env = CandleAiEnvironment()
    try:
        latest_policy = max(
            glob.glob(f"{env.metadata['name']}_world_*.zip")
        )
    except ValueError:
        print("Policy not found.")
        return

    model = PPO.load(latest_policy)

    rewards = {a: 0 for a in env.possible_agents}

    for i in range(num_games):
        env.reset()
        env.action_space(env.possible_agents[0])

        for agent in env.agent_iter():
            obs, reward, termination, truncation, info = env.last()

            actions = {}
            for a in env.agents:
                rewards[a] += env.rewards[a]
                if termination or truncation:
                    break
                else:
                    if agent == env.possible_agents[0]:
                        actions[agent] = env.action_space(agent).sample()
                    else:
                        actions[agent] = model.predict(obs, deterministic = True)[0]
            env.step(actions)

        env.close()

        avg_reward = sum(rewards.values()) / len(rewards.values())
        avg_reward_per_agent = {
            agent: rewards[agent] / num_games for agent in env.possible_agents
        }
        print(f"Avg reward: {avg_reward}")
        print("Avg reward per agent, per game: ", avg_reward_per_agent)
        print("Full rewards: ", rewards)
        return avg_reward


