import json
import os
import logging

logger = logging.getLogger(__name__)

# LOAD TOKEN
with open("config.json") as config:
    logger.info(">>> Loading Token ... ")
    data = json.load(config)
    token = data["TOKEN"]

# LOAD TOKEN
os.environ["TOKEN"] = token
logger.info(">>> Token in Environment ... ")
