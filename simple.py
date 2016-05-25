import drone
import configparser
import sys

configs = []
for configfile in sys.argv[1:]:
	config = configparser.ConfigParser()
	config.read("data/" + configfile + ".ini")
	configs.append(config)
drone.run_codrone(configs)
