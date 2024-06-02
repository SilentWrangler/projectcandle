from ai.candle_ai_env import CandleAiEnvironment as CAEI

from pettingzoo.test import parallel_api_test

def envtest():
    env = CAEI()
    parallel_api_test(env, num_cycles = 100)

