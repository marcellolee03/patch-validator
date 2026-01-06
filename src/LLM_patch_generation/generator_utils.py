from dotenv import load_dotenv
from os import getenv
from dataclasses import dataclass
from openai import OpenAI
from os import makedirs


def generate_prompt(vulnerability_details: dict, environment_info: str) -> dict:
    vulnerability_info = ''
    for key, value in vulnerability_details.items():
        vulnerability_info += f'{key}: {value}\n'

    return { 
"CVEs": vulnerability_details["CVEs"],

"prompt": f''' 
You are a senior security engineer specialized in the creation of BASH shell scripts.

Your task is to generate a safe, idempotent, auditable BASH shell script capable of correcting the following vulnerability once executed on the target system.

## VULNERABILITY INFORMATION:
{vulnerability_info}

## COMPUTATIONAL ENVIRONMENT INFORMATION:
{environment_info}

Your response MUST follow this exact structure, with each section clearly defined:

## 1. Environment Analysis
- **System Compatibility:** Analyze the provided environment information and confirm compatibility with the remediation approach. Identify any environment-specific considerations (e.g., package manager commands, init system, kernel version requirements).
- **Prerequisites Check:** List any missing dependencies or tools that need to be verified or installed based on the environment.
- **Potential Conflicts:** Identify any installed software, running services, or system configurations that might conflict with the remediation.

---

## 2. Vulnerability Analysis
- **Description:** Explain what the vulnerability is in simple terms.
- **Impact:** Describe the potential risks and impact if the vulnerability is exploited.
- **Detection:** Detail the specific commands or checks that can be used to confirm the system is currently vulnerable, adapted to the detected environment (e.g., using the correct package manager commands).
- **Affected Components:** Identify which specific software versions or configurations in the environment are vulnerable.

---

## 3. Remediation Plan
- **Strategy:** Describe the step-by-step plan to fix the vulnerability. Explain why this is the optimal approach for the detected environment.
- **Environment-Specific Adaptations:** Explain any adjustments made based on the OS version, package manager, init system, or other environment factors.
- **Pre-flight Checks:** List the checks the script will perform before making any changes (e.g., verifying root privileges, checking if the fix is already applied, validating package manager availability, confirming required services are running).
- **Safety Measures:** Explain the safety mechanisms that will be included (e.g., backing up configuration files before modifying them, testing configurations before applying, providing rollback capability).
- **Verification:** Describe how the script will confirm that the fix was successfully applied and that the system remains functional.

---

## 4. Generated BASH Script
Generate the final BASH script based on the plan above. The script MUST adhere to the following best practices:

- **Shebang:** Start with `#!/bin/bash`.
- **Error Handling:** Use `set -euo pipefail` to ensure the script exits immediately if a command fails, and include trap handlers for cleanup on error.
- **Environment Detection:** Include functions to validate the environment matches expected parameters (OS, package manager, required tools).
- **Idempotency:** The script must be safe to run multiple times. If it detects the system is already secure, it should report that and exit gracefully with appropriate exit codes.
- **Auditability & Logging:** 
  - Include clear `echo` statements for each major action with timestamps
  - Log all actions to a file (e.g., `/var/log/vulnerability_remediation_YYYYMMDD.log`)
  - Distinguish between INFO, WARNING, and ERROR messages
- **Privilege Management:** Check for and require appropriate privileges (typically root) with clear error messages if not met.
- **Backup & Rollback:** Create timestamped backups of any files modified, and provide instructions for rollback if needed.
- **Comments:** Add detailed comments within the code explaining the purpose of each function or command block.
- **Exit Codes:** Use meaningful exit codes (0 = success, 1 = already patched, 2 = error, etc.) and document them.

The script should be production-ready, defensive, and assume it may run in an automated environment.

Your response should only contain the generated shell script. Nothing else.
'''}


load_dotenv(override = True)

@dataclass
class ApiResponseStatus:
    status: str
    content: str


def ask_LLM(model: str, prompt: str) -> ApiResponseStatus:
    match model:
        case 'deepseek-R1':
            API_URL = "https://openrouter.ai/api/v1"
            MODEL = "deepseek/deepseek-r1-0528:free"
            API_KEY = getenv('DEEPSEEK_API_KEY')
        case 'deepseek-V3.1':
            API_URL = "https://openrouter.ai/api/v1"
            MODEL = "deepseek/deepseek-chat-v3.1"
            API_KEY = getenv('DEEPSEEK_API_KEY')
        case 'gemini-2.5-pro':
            API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
            MODEL = "gemini-2.5-pro"
            API_KEY = getenv('GEMINI_API_KEY')
        case 'gemini-2.5-flash':
            API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
            MODEL = "gemini-2.5-flash"
            API_KEY = getenv('GEMINI_API_KEY')
        case 'gpt-5.1':
            API_URL = None
            MODEL = 'gpt-5.1'
            API_KEY = getenv('GPT_API_KEY')
        case _:
            return ApiResponseStatus(
                status='ERR',
                content=f'Invalid LLM model: {model}'
            )

    if not API_KEY:
        return ApiResponseStatus(
            status='ERR',
            content='DEEPSEEK_API_KEY environment variable not set.'
        )
    
    elif API_URL == None:
        client = OpenAI(
            api_key=API_KEY
        )

    else:
        client = OpenAI(
            base_url=API_URL,
            api_key=API_KEY,
        )


    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ]
        )

        return ApiResponseStatus(
            status='OK',
            content=response.choices[0].message.content
        )
    except Exception as e:
        return ApiResponseStatus(
            status='ERR',
            content=f'{str(e)}'
        )
    

def save_results(CVEs: str, LLM_model: str, generated_patch: str, elapsed_time: float):

    base_path = f'patches/{CVEs}'

    try:
        makedirs(base_path)
    except FileExistsError:
        pass


    patch_file = base_path + f'/{LLM_model}_patch.sh'
    details_file = base_path + f'/{LLM_model}_details.txt'

    print(f'Saving correction patch in: {patch_file}')
    with open(patch_file, 'w') as f:
        f.write(generated_patch)
    
    print(f'Saving patch generation details in: {details_file}')
    with open(details_file, 'w') as f:
        f.write('=== PATCH GENERATION DETAILS ===\n')
        f.write(f'Model: {LLM_model}\n')
        f.write(f'Vulnerability: {CVEs}\n')
        f.write(f'Time elapsed: {elapsed_time:.4f} seconds\n')
        f.write(f'Patch functional?: ')
