import os
import subprocess
import re
import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser("CreateTerraformInterface")
parser.add_argument("-p",
                    "--path",
                    help="path to directory that you want to search",
                    type=str
                    )
parser.add_argument("-n", "--name",
                    help="name of the file that you want to search for",
                    type=str,
                    default=".build-interface.here"
                    )
parser.add_argument("-s", "--state",
                    type=str2bool,
                    nargs='?',
                    const=True,
                    default=True,
                    help="Defaulted to true, if set to false will not create the state.tf file."
                    )
args = parser.parse_args()


def find_files_in_directory(root_dir, target_filename):
    matching_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == target_filename:
                matching_files.append(os.path.abspath(os.path.join(root, file)))
    return matching_files

def format_outputs(folder_path):
    output_file = os.path.join(folder_path, "interface", "outputs.tf")

    script_filename = os.path.basename(__file__)

    output_blocks = []

    for root, dirs, files in os.walk(folder_path):
        if root == folder_path:  # Only process files in the root of module_path
            for file in files:
                if file != script_filename and file.endswith(".tf"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        content = f.read()
                        matches = re.findall(r'output\s+"([^"]+)"', content)
                        for match in matches:
                            output_blocks.append(match)

    output_blocks = sorted(output_blocks)

    # Delete the existing output file and create a new one
    # open(output_file, "w").close()
    with open(output_file, "w") as file:
        file.truncate(0)

    # Write the new output content
    with open(output_file, "w") as f:
        for block in output_blocks:
            f.write(f'output "{block}" {{\n')
            f.write(f'  value = data.terraform_remote_state.state.outputs.{block}\n')
            f.write("}\n\n")
    return None


def format_state(folder_path):
    module_path = folder_path
    state_file = os.path.join(module_path, "interface", "state.tf")

    script_filename = os.path.basename(__file__)

    backend_config = {}

    for root, dirs, files in os.walk(module_path):
        if root == module_path:  # Only process files in the root of module_path
            for file in files:
                if file != script_filename and file.endswith(".tf"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        content = f.read()
                        matches = re.findall(r'backend\s+"([^"]+)"\s+{(.+?)}', content, re.DOTALL)
                        for match in matches:
                            backend_type = match[0].strip()
                            config_content = match[1]
                            config = {}
                            for line in config_content.split("\n"):
                                line = line.strip()
                                if "=" in line:  # Ensure the line has an equal sign
                                    key, value = map(str.strip, line.split("=", 1))
                                    # Remove extra double quotes from the value
                                    value = value.strip('"')
                                    config[key] = value
                            backend_config[backend_type] = config

    # Delete the existing state file and create a new one
    # open(state_file, "w").close()
    with open(state_file, "w") as file:
        file.truncate(0)

    # Write the new state content
    with open(state_file, "w") as f:
        for backend_type, config in backend_config.items():
            f.write(f'data "terraform_remote_state" "state" {{\n')
            f.write(f'  backend   = "{backend_type}"\n')
            f.write(f'  workspace = var.workspace == "" ? terraform.workspace : var.workspace\n\n')
            f.write('  config = {\n')
            for key, value in config.items():
                f.write(f'    {key} = "{value}"\n')
            f.write('  }\n')
            f.write('}\n\n')
    return None


def build_variables(folder_path):
    folder_path = folder_path
    variable_file = os.path.join(folder_path, "interface", "variables.tf")

    script_filename = os.path.basename(__file__)

    # truncate the existing variable file
    with open(variable_file, "w") as file:
        file.truncate(0)

    text = """
variable "workspace" {
  type        = string
  default     = ""
  description = "environment + location of the environment"
}

    """

    # Write the new state content
    with open(variable_file, "w") as f:
        f.write(text)
    return None


def main():
    print(os.getcwd())
    target_filename = args.name
    root_directory = args.path
    matching_files = find_files_in_directory(root_directory, target_filename)

    if not matching_files:
        print("No matching files found.")
        return

    for file_path in matching_files:
        print(f"Found the file at: {file_path}")
        folder_path = os.path.dirname(file_path)
        interface_folder_path = os.path.join(folder_path, "interface")

        # check to see if the interfaces folder exists already
        if not os.path.exists(interface_folder_path):
            os.makedirs(interface_folder_path)
            print(f"Folder '{interface_folder_path}' created successfully.")
        else:
            print(f"Folder '{interface_folder_path}' already exists.")

        # Pass the file path to the execute_me.py script
        # execute_script_path = "execute_me.py"  # Change this if the script is in a different location
        # subprocess.run(["python3", execute_script_path, found_file_path])
        format_outputs(folder_path)
        format_state(folder_path)
        build_variables(folder_path)

if __name__ == "__main__":
    main()
