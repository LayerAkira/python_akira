# LayerAkira SDK
Simple SDK of utilities and clients to interact  with LayerAkira exchange


To interact with exchange user can use following clients:

1) `HttpClient` -- to interact with http endpoints of exchange and smart contracts
2) `WsClient` -- to subscribe for various streams of exchange
3) `CLIClient` -- to interact with exchange in CLI-like fashion 


Executables folder contains runners for interaction with exchange:

*) `executables/run_cli_client.py` using CLIClient to interact with exchange in CLI like fashion.  Through such interaction one can learn how to interact with exchange to build more sophisticated connectors for trading

To install through pip (https://packaging.python.org/en/latest/guides/using-testpypi/) use the following command:

<code> python3 -m pip install --index-url https://test.pypi.org/project LayerAkira </code>