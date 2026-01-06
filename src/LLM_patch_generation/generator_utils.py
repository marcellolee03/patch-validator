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
Role: Act as a Senior System Security Engineer and Linux Hardening Specialist.

## VULNERABILITY CONTEXT:
{vulnerability_info}

## COMPUTATIONAL ENVIRONMENT CONTEXT:
{environment_info}

Task: Write a minimalist, surgical, and idempotent BASH script to mitigate the vulnerability described above within the provided environment context.

Code Requirements:

-Minimalism: Use only native commands (preferably POSIX-compliant). Avoid installing new packages unless strictly necessary.

-Surgical Logic: The script must:

--Validate whether the system is vulnerable before taking action.

--Apply the exact fix (e.g., change a permission, edit a config line, disable a service).

--Clean Code: Use semantic variable names, clear indentation, and brief comments only where the logic is complex.

--Security: Implement basic error handling (e.g., set -euo pipefail) and verify that the user has root privileges.

--Output: The script must be silent on success, reporting errors only via stderr.

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
        case 'gemini-3-flash':
            API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
            MODEL = "gemini-3-flash-preview"
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
