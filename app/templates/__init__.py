from pathlib import Path

from jinja2 import Environment, FileSystemLoader

template_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent),
    enable_async=True,
)
