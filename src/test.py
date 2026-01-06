
from LLM_patch_generation.generator_utils import generate_prompt, ask_LLM, save_results

print(ask_LLM('deepseek-R1', 'generate me a correction patch capable of mitigating the vulnerability cve-1999-0497').content)
