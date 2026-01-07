from LLM_patch_generation.generator_utils import generate_prompt, ask_LLM, save_results
from LLM_patch_generation.args_parser import parse_arguments_generator
from LLM_patch_generation.extract_info.container_scanner import extract_container_info, list_containers
from LLM_patch_generation.extract_info.env_scanner import extract_environment_info
from LLM_patch_generation.extract_info.vuln_details_extractor import extract_vulnerability_details, get_found_vulnearbilities
from AutoVAS.fully_initiate_scan import fully_initiate_scan
from LLM_patch_generation.validator_utils import search_for
import time

def main():
    #scan_report = fully_initiate_scan()
    args = parse_arguments_generator()

    LLM_model = args.LLM_model
    scan_report_filepath = args.report_filepath

    found_vulnerabilities = get_found_vulnearbilities(scan_report_filepath)

    # Prompting user to select a vulnerability to mitigate.
    valid_user_input = False
    while not valid_user_input:
        print('Select a vulnerability to fix from the following list:')
        for key, value in found_vulnerabilities.items():
            print(f'{key} - [{value}]')

        user_input = input()

        try:
            user_input = int(user_input)
            if user_input in found_vulnerabilities:
                valid_user_input = True
                vulnerability_loc = user_input
        except ValueError:
            pass
    
    # Prompting user to say if vulnerability is found in DOCKER CONTAINER 
    valid_user_input = False
    while not valid_user_input:
        user_input = input('Is vulnerability found in a Docker Container [Y/n]? ')
        
        match user_input.lower():
            case 'y':
                vuln_in_container = True
                valid_user_input = True
            case 'n':
                vuln_in_container = False
                valid_user_input = True
            case _:
                pass

    print('Extracting environment information...')
    if vuln_in_container:
        active_containers = list_containers()
        
        print('Select container from list: ')
        for container in active_containers:
            print(f'- {container}')
        
        valid_user_input = False
        while not valid_user_input:
            user_input = input()

            if user_input in active_containers:
                env_info = extract_container_info(user_input)
                valid_user_input = True
            else:
                print('Invalid input. Select container from list')
    else:
        environment_pattern = r"^\s*\"" + "pop-os-24-ambient" + r"\":\s*\{(.*?)\}"
        match = search_for(environment_pattern, 'env_info.txt')
        
        if match:
            env_info = match
        else:
            print("Target vulnerability not found in env_info.txt. Ending program.")
            return

#        env_info = extract_environment_info()

    print('Extracting vulnerability details...')
    vuln_details = extract_vulnerability_details(scan_report_filepath, vulnerability_loc)

    print('Generating prompt...')
    prompt = generate_prompt(vuln_details, env_info)

    # Patch generation and elapsed time calculation
    print(f'Awaiting {LLM_model} api response...')

    timer_start = time.perf_counter()
    
    LLM_response = ask_LLM(LLM_model, prompt["prompt"])
    
    timer_end = time.perf_counter()
    elapsed_time = (timer_end - timer_start)

    if LLM_response.status == "ERR":
        print(f"ERROR while fetching {LLM_model} response. Shutting down script.")
        print(f"ERROR details: {LLM_response.content}")
        return
    
    # Saving results 
    print("Saving results...")
    save_results(prompt["CVEs"], LLM_model, LLM_response.content, elapsed_time)
    
if __name__ == "__main__":
    main()
