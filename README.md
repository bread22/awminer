# awminer
This is a auto switch crypto currency miner on zpool.ca for windows user.
It only support NVIDIA GPU and zpool at this time.

It is developed on Python 2.7, and needs selenium and PhamtomJS

Download PhamtomJS windows binary and put it in C:\Users\username\AppData\Local\Microsoft\WindowsApps, or any folder your PATH can find

You need below miner binary
ccminerAlexis78.exe			- https://github.com/alexis78/ccminer
ccminerTanguy.exe			- https://github.com/tpruvot/ccminer

You can use any ccminer forks

Usage:

1. Edit mining_machine.json to your wallet/name/interval, switch_interval is in minuted
2. Edit your own hashrate for each algorithm in algos_zpool.json, default values are for GTX 1080 Ti. If you want to skip specific algo, set hashrate to 0
3. run 'python start.py' from cmd window, scraping zpool for current profit take about 2 minutes, don't panic
