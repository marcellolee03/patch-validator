import subprocess
import platform

def run_command(cmd) -> str:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        return f'Error: {str(e)}'
    

def get_os_info() -> dict:
    return {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
    }


def get_kernel_info() -> dict:
    return {
        'kernel_name': run_command('uname -s'),
        'kernel_version': run_command('uname -r')
    }


def detect_package_manager() -> dict:
    managers = {}

    pm_commands = {
        'apt': 'apt --version 2>/dev/null',
        'apt-get': 'apt-get --version 2>/dev/null',
        'yum': 'yum --version 2>/dev/null',
        'dnf': 'dnf --version 2>/dev/null',
        'zypper': 'zypper --version 2>/dev/null',
        'pacman': 'pacman --version 2>/dev/null',
        'apk': 'apk --version 2>/dev/null',
        'rpm': 'rpm --version 2>/dev/null',
        'dpkg': 'dpkg --version 2>/dev/null'
    }

    for pm, cmd in pm_commands.items():
        result = run_command(cmd)
        if result and 'Error' not in result and result != '':
            managers[pm] = {
                'available': True,
                'version': result.split('\n')[0] if result else 'unknown'
            }
    
    primary = None
    if 'apt' in managers or 'apt-get' in managers:
        primary = 'apt'
    elif 'dnf' in managers:
        primary = 'dnf'
    elif 'yum' in managers:
        primary = 'yum'
    elif 'zypper' in managers:
        primary = 'zypper'
    elif 'pacman' in managers:
        primary = 'pacman'
    elif 'apk' in managers:
        primary = 'apk'
    
    return {
        'primary_manager': primary,
        'available_managers': managers,
    }


def get_installed_packages(limit=None) -> dict:
    packages = {
        'count': 0,
        'packages': [],
        'method': None
    }
    
    commands = {
        'dpkg': "dpkg -l | grep '^ii' | awk '{print $2, $3}'",
        'rpm': "rpm -qa --queryformat '%{NAME} %{VERSION}-%{RELEASE}\n'",
        'pacman': "pacman -Q",
        'apk': "apk info -v"
    }
    
    for method, cmd in commands.items():
        result = run_command(cmd)
        if result and 'Error' not in result and result != '':
            packages['method'] = method
            lines = result.split('\n')
            packages['count'] = len(lines)
            
            if limit:
                packages['packages'] = lines[:limit]
                packages['note'] = f'Showing first {limit} of {len(lines)} packages'
            else:
                packages['packages'] = lines
            break
    
    return packages


def extract_environment_info() -> str:
    environment_info = ''

    # Writing os information
    environment_info += '\n**OS INFO**:\n'
    os_info = get_os_info()
    for key, value in os_info.items():
        environment_info += f'{key}: ({value})\n'

    # Writing kernel information
    environment_info += '\n**KERNEL INFORMATION**:\n'
    kernel_info = get_kernel_info()
    for key, value in kernel_info.items():
        environment_info += f'{key}: ({value})\n'

    # Writing package manager information
    environment_info += '\n**PACKAGE MANAGER INFORMATION**:\n'
    package_manager_info = detect_package_manager()
    
    environment_info += f'Primary Manager: ({package_manager_info['primary_manager']})\n'

    return environment_info
