from typing import Annotated

import typer

from client.utils.config import logger


def cli(
        help: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        exit: Annotated[str, typer.Option(..., "--exit", help="exit")] = "",
        session: Annotated[str, typer.Option(..., "--session", help="session")] = "",
        interact: Annotated[str, typer.Option(..., "--interact", help="interact")] = "",
        agent:  Annotated[str, typer.Argument(..., "--agent", help="agent")] = "",

):
        server = "rat > "
        while choice != exit:
            logger


        #https://packaging.python.org/en/latest/guides/creating-command-line-tools/"