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
Role:
You are a Senior Security Engineer and Linux Kernel Maintainer with decades of experience in code analysis, incident response, and patch management.
Your primary responsibility is to ensure the stability, performance, and security of production systems. 

Task:
You have received four (4) patches that all claim to fix the **same** security vulnerability. 
Your mission is to conduct an in-depth comparative analysis and **determine which patch is the best solution** to apply in production, justifying your choice in a technical and didactic manner.
If NONE of the proposed correction patches successfully mitigate the specified vulnerability, you should declare NONE as the verdict.
---

# AVAILABLE INFORMATION:
## VULNERABILITY CONTEXT:
{vuln_details}

## COMPUTATIONAL ENVIRONMENT CONTEXT:
{env_info}

## IDEAL SOLUTION:
{vuln_cheats}

---
# PROPOSED CORRECTION PATCHES:
{generated_patches}
---

# Analysis Instructions and Output Format:

Think step-by-step. For each of the four patches, rigorously evaluate them based on the following criteria:

## Evaluation Criteria (Your Thought Process)

1.  **Fix Efficacy:**
    * Does the patch *completely* fix the described root cause?
    * Does it align with the provided "Ideal Fix"?
2.  **Regression Risk (Security):**
    * Does the patch inadvertently introduce **new vulnerabilities**? (Ex: integer overflows, off-by-one errors, new race conditions, incorrect validations)?
3.  **Regression Risk (Stability):**
    * Could the patch cause *kernel panics*, *deadlocks*, or break existing functionality in the critical services (Nginx, PostgreSQL)?
4.  **Performance Impact:**
    * Does the fix introduce significant *overhead*? (Ex: Adds unnecessary locks, excessive loops, or redundant checks in a *hot path* of the code?)
5.  **Maintainability and Code Quality:**
    * Is the code clean, does it follow the Linux *coding style*, and is it well-commented?

### Expected Output Format

Provide your answer in the following format:

**Verdict:** `[Patch X]`

**Summary Justification:**
`[A brief (2-3 line) explanation of why Patch X was chosen and why the others were rejected, taking the Security Policy into account.]`

---

**Patch Analysis:**

**Patch by [AUTHOR NAME]:**
* **Efficacy:**: (1 - (YES/NO)), (2 - (YES/NO))
* **Risk (Security/Stability):** (YES/NO)
* **Performance:** (YES/NO)
* **Maintainability:** (YES/NO)

** (Repeat structure) **
"""
