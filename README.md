GPIG5 drone
===========

To run the drone copy `config.ini.dist` to `config.ini` and set the parameters for your environment server and drones.

Run with `python drone.py` using Python 3.4+

Options:
    config <config-file> - runs the drone(s) based on the specified config.
    multi - spawns multiple drones on the same python thread
    multi fork <x> - spawns multiple drones on different processes (only works in windows atm). x is the number of drones.

