import re
import yaml

def conda_env_to_requirements(input_file, output_file):
    with open(input_file, 'r') as f:
        conda_env = yaml.safe_load(f)

    with open(output_file, 'w') as f:
        if 'dependencies' in conda_env:
            for dependency in conda_env['dependencies']:
                if isinstance(dependency, str):
                    # Use a regular expression to match the package name and version
                    match = re.match(r'([\w\-]+)([>=<]+)?(\d+\.\d+\.\d+)?', dependency)

                    if match:
                        # Extract the package name, relation, and version
                        package_name, relation, package_version = match.groups()

                        # If there's no relation and version, just write the package name
                        if relation is None and package_version is None:
                            f.write(package_name + '\n')
                        else:
                            f.write(f"{package_name}{relation}{package_version}\n")

