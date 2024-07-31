from dataclasses import dataclass

import yaml

@dataclass
class AdminConfig:
    email: str
    password: str

@dataclass
class BotConfig:
    token: str
    group_id: int

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


with open("etc/config.yaml", "r") as f:
    raw_config = yaml.safe_load(f)

db_config = DatabaseConfig(
    host=raw_config["database"]["host"],
    port=raw_config["database"]["port"]
)

config = {
    "name": raw_config["bot"]["name"],
    "API_token": raw_config["bot"]["API_token"],
    "admin_id": raw_config["admin"]["telegram_id"],
    "ip_mongo_database": raw_config["database"]["host"],
    "port_mongo_database": raw_config["database"]["port"]
}

config_gymchana_cup = {
    "site":  raw_config["gymkhana_cup"]["site"],
    "API": raw_config["gymkhana_cup"]["API"],
    "GET_TIME_OUT": raw_config["gymkhana_cup"]["GET_TIME_OUT"],
    "trackUrl": raw_config["gymkhana_cup"]["trackUrl"],
    "best_time": None
}
