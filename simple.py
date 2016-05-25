import drone
import configparser
import sys


config = configparser.ConfigParser()
config.read(sys.argv[1])
drone.run_drone(config)
















