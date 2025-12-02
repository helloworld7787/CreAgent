import yacs.config as config
from tqdm import tqdm
import time

# cnf = config.CfgNode()
# cnf.set_new_allowed(True)
# cnf.merge_from_file('config/config.yaml')
# # print(cnf)
# print(cnf.llm_model_name)

for i in tqdm(range(10), colour='green'):
    print(i)
    time.sleep(1)