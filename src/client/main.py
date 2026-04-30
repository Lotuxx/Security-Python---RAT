from server.utils import ui
import typer


def main():
    app = typer.Typer()
    app.command()(cli)

if __name__ == "__main__":
    main()
