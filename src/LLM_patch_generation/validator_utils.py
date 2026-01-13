import re

def search_for(pattern_string, target_file):
    try:
        with open(target_file, 'r') as f:
            target_file_content = f.read()
    except FileNotFoundError:
        print(f'Could not locate {target_file}. Ending program.')
        return

    pattern = re.compile(pattern_string, re.DOTALL | re.MULTILINE)
    match = pattern.search(target_file_content)
    
    if match:
        return match.group(1).strip()
    else:
        return None
    
    
def generate_validator_prompt(env_info, vuln_details, vuln_cheats, generated_patches):
    return f"""
# Role:
You are a **Senior Security Engineer** and **Linux Kernel Maintainer**. Your expertise lies in deep code analysis, identifying side effects, and ensuring that security patches adhere to the highest standards of performance and stability.

# Task:
Analyze four (4) proposed patches designed to fix a specific security vulnerability. 
Your goal is to evaluate each patch against the provided context and the "Ideal Solution," assign a score, and determine the winner(s).

# Evaluation Methodology:
For each patch, you must perform a "Step-by-Step Analysis" BEFORE assigning the final score:
1. **Vulnerability Fix:** Does it effectively neutralize the root cause described in the OpenVAS report?
2. **Computational Compatibility**: Is the patch compatible with the specified Computational Environment (e.g, uses missing dependencies)?
3. **Side Effects:** Does the patch introduce potential performance regressions or new security risks?
4. **Alignment:** How closely does the logic follow the "Ideal Solution"?

# Scoring Rubric:
* **Score 1 (Failed):** The patch does NOT fix the vulnerability, is syntactically incorrect, is incompatible with the specified Computational Environment, or would fail to compile/run in the specified environment.
* **Score 2 (Sub-optimal Fix):** The patch successfully fixes the vulnerability but uses a "workaround" logic, introduces technical debt, or deviates significantly from the best practices outlined in the Ideal Solution.
* **Score 3 (Optimal Fix):** The patch effectively fixes the vulnerability, follows the logic of the Ideal Solution, and maintains code quality/performance standards.

---
# INPUT DATA:
## VULNERABILITY CONTEXT:
{vuln_details}

## COMPUTATIONAL ENVIRONMENT:
{env_info}

## IDEAL SOLUTION (Reference):
{vuln_cheats}

## PROPOSED PATCHES TO EVALUATE:
{generated_patches}

---
# Expected Output Format:

### Patch Analysis: [Patch ID/Author]
**Analysis:** [Briefly explain if it fixes the issue and if there are side effects]
**Alignment Check:** [Compare logic with the Ideal Solution]
**Score:** [1, 2, or 3]

---
**Final Winner(s):** [Patch X, Patch Y] (or "NONE" if all scored 1)
"""
