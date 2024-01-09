

import argparse
import asyncio

from LayerAkira.src.CLIClient import CLIClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='CliClient', description='Interact with LayerAkira')
    parser.add_argument('--toml_config_file', default='run_cli_cfg.toml')
    args = parser.parse_args()
    asyncio.get_event_loop().run_until_complete(CLIClient.start(args.toml_config_file))
