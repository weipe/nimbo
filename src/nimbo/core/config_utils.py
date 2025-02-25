import os
import yaml

from nimbo.core.paths import CONFIG

VALID_FIELD_NAMES = [
    "local_results_path",
    "local_datasets_path",
    "s3_results_path",
    "s3_datasets_path",
    "aws_profile",
    "region_name",
    "instance_type",
    "spot",
    "spot_duration",
    "image",
    "disk_size",
    "conda_env",
    "run_in_background",
    "persist",
    "security_group",
    "instance_key",
]

ALL_REQUIRED_FIELDS = [
    "local_results_path",
    "local_datasets_path",
    "s3_results_path",
    "s3_datasets_path",
    "aws_profile",
    "region_name",
    "instance_type",
    "spot",
    "image",
    "disk_size",
    "conda_env",
    "run_in_background",
    "persist",
    "security_group",
    "instance_key",
]


def load_config():
    # Load yaml config file
    if not os.path.isfile(CONFIG):
        raise FileNotFoundError(
            f"Nimbo configuration file '{CONFIG}' not found.\n"
            "You can run 'nimbo generate-config' to create a default config file."
        )

    with open(CONFIG, "r") as f:
        config = yaml.safe_load(f)
    return config


class ConfigVerifier:
    def __init__(self, config):
        self.config = config

    def verify(self, required_fields="all", fields_to_check="all"):
        # These functions must be ran in this order
        self.check_field_names()
        self.check_required_fields(required_fields)
        self.check_field_values(fields_to_check)

        # if self.config["disk_size"] < 128:
        #    raise ValueError("Disk size must be greater than 127Gb.")

    def check_required_fields(self, required_fields):
        if required_fields == "all":
            required_fields = ALL_REQUIRED_FIELDS

        missing_fields = []

        for field in required_fields:
            if field not in self.config:
                missing_fields.append(field)

        if len(missing_fields) > 0:
            raise KeyError(
                f"Some required nimbo-config.yml fields are missing: {missing_fields}"
            )

    def check_field_names(self):
        # Set of elements that are in config.keys() but not in VALID_FIELDS
        invalid_fields = set(self.config.keys()).difference(set(VALID_FIELD_NAMES))
        if len(invalid_fields) > 0:
            raise KeyError(f"Invalid nimbo-config.yml fields: {list(invalid_fields)}")

    def check_field_values(self, fields_to_check):
        if fields_to_check == "all":
            fields_to_check = ["instance_key", "conda"]

        for field in fields_to_check:
            getattr(self, f"check_{field}")()

    def check_instance_key(self):
        instance_key_name = self.config["instance_key"]
        if not os.path.isfile(instance_key_name + ".pem"):
            raise FileNotFoundError(
                f"The instance key file '{instance_key_name}.pem' was not found in the current directory.\n"
                "Make sure the file exists, or see https://docs.nimbo.sh/getting-started#create-instance-key-pairs "
                "for instructions on how to get one."
            )

    def check_conda(self):
        conda_env = self.config["conda_env"]
        if not os.path.isfile(conda_env):
            raise FileNotFoundError(
                f"Conda env file '{conda_env}' not found in the current folder."
            )


def fill_defaults(config):
    # Modifies dictionary in place
    config_defaults = {
        "spot": False,
        "image": "ubuntu18-latest-drivers",
        "disk_size": 128,
        "run_in_background": False,
        "persist": False,
        "security_group": "default",
    }
    for key, value in config_defaults.items():
        if key not in config:
            config[key] = value


def remove_trailing_backslashes(config):
    # Modifies dictionary in place
    fields = [
        "local_datasets_path",
        "local_results_path",
        "s3_datasets_path",
        "s3_results_path",
    ]

    for field in fields:
        config[field] = config[field].strip("/")


def generate_config(quiet=False):
    config = """# Data paths
local_datasets_path: my-datasets-folder  # relavtive to project root 
local_results_path: my-results-folder  # relative to project root
s3_datasets_path: s3://my-bucket/my-project/some-datasets-folder
s3_results_path: s3://my-bucket/my-project/some-results-folder

# Device, environment and regions
aws_profile: default
region_name: eu-west-1
instance_type: p2.xlarge
spot: no

image: ubuntu18-latest-drivers
disk_size: 128
conda_env: my-conda-file.yml

# Job options
run_in_background: no
persist: no

# Permissions and credentials
security_group: default
instance_key: my-ec2-key-pair  # without .pem """

    with open("nimbo-config.yml", "w") as f:
        f.write(config)

    if not quiet:
        print("Example config written to nimbo-config.yml.")
