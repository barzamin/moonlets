#!/usr/bin/env python3
import click
import xml.etree.ElementTree as ElTr

@click.command()
@click.argument('XMLFILE', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def cli(xmlfile):
	try:
		_ = ElTr.parse(xmlfile)
	except ElTr.ParseError as e:
		click.echo(click.style(f'linting {xmlfile} failed:', fg='red') + f' {e}')

if __name__ == '__main__':
	cli()