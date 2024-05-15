import click


@click.command()
@click.argument('mode', type=click.Choice(['login', 'flags']))
def main(mode):
    """Posthog CLI"""
    if mode == 'login':
        click.echo("Login mode selected")
        # Add your login logic here
    elif mode == 'flags':
        click.echo("Flags mode selected")
        # Add your flags logic here
    else:
        click.echo("Invalid mode selected")


if __name__ == "__main__":
    main()

