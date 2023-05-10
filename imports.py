import configparser

config = configparser.ConfigParser()
config.read('config.ini')

ELMO_OPTIONS_FILE = config['DEFAULT']['ElmoOptionsFile']
ELMO_WEIGHT_FILE = config['DEFAULT']['ElmoWeightFile']
STANFORDCORENLP = config['DEFAULT']['STANFORDCORENLP']

VOCABS_CONFIG = config['VOCAB']
EVALUATION_CONFIG = config['EVALUATION']