# awminer
This is a auto switch crypto currency miner on zpool.ca for windows user.
It only support NVIDIA GPU at this time.

It is develop on Python 2.7, and needs PyQt4

Usage:

1. Edit mining_machine.json to your wallet/name/interval
2. Edit hashrate in algos_zpool.json, default values are for GTX 1080 Ti. If you want to skip specific algo, set hashrate to 0
3. run 'python start.py' from cmd window
