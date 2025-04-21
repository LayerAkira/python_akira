

import argparse
import asyncio
import logging

from LayerAkira.src.CLIClient import CLIClient
from LayerAkira.src.hasher.Hasher import AppDomain

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='CliClient', description='Interact with LayerAkira')
    parser.add_argument('--toml_config_file', default='run_cli_cfg.toml')
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename='logs_cli.txt')

    async def main():
        cli_client = CLIClient(args.toml_config_file)
        await cli_client.start(AppDomain(cli_client.cli_cfg.chain_id.value))

    asyncio.get_event_loop().run_until_complete(main())



# place_order ETH/STRK 1945 0.0000006 0 BUY  LIMIT 1 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/STRK 1944 0.0000006 0 BUY  LIMIT 1 0 0 ROUTER 0 INTERNAL 0

# place_order ETH/USDC 1944 0.0000011 0 SELL LIMIT 0 0 0 ROUTER 0 INTERNAL 0



# place_order ETH/USDC 250100 0 0.200000 SELL LIMIT 1 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/STRK 258403 0 0.516806 BUY MARKET 0 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/USDC 249803 0 0.250000 BUY LIMIT 1 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/USDC 249900.4 0 0.150000 SELL LIMIT 1 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/USDC 258403 0 0.516806 BUY MARKET 0 0 0 ROUTER 0 INTERNAL 0
# place_order ETH/USDC 244003 0 0.488006 SELL MARKET 0 0 0 ROUTER 0 INTERNAL 0

# place_order ETH/STRK 1945 0.0000006 0 SELL  MARKET 0 0 0 ROUTER 0 INTERNAL 0