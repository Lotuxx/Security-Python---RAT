from typing import Annotated

import typer


def cli(
        help: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        download: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        upload: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        shell: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        ipconfig: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        screenshot: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        search: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        hashdump: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        keylogger: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        webcam_snapshot: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        webcam_stream: Annotated[str, typer.Option(..., "--url", help="url")] = "",
        record_audio: Annotated[str, typer.Option(..., "--url", help="url")] = "",

):
        server = "rat > "
        start = (" BEGINNING SERVER, \n"
                  "Listening on 8888... ")

        for i in range(0, count):
                print(server)

        #https://packaging.python.org/en/latest/guides/creating-command-line-tools/"