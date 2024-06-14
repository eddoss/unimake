from umk.kit import config
from umk.core import Field


@config.register
class Config(config.Interface):
    py: str = Field("python3", description="Which python is used")
