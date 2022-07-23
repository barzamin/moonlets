#!/usr/bin/env python3

import struct
import click
import itertools
import shutil
from dataclasses import dataclass
from rich.progress import Progress
from pathlib import Path

def read_fixed_str(f, length):
	bb = f.read(length)
	return bytes(itertools.takewhile(lambda b: b != 0x00, bb)).decode('ascii')

@dataclass
class FileDescriptor:
	name: str
	size: int
	padded_size: int
	offset: int

def read_descriptor(f):
	name = read_fixed_str(f, length=0x34)
	size, padded_size, offset = struct.unpack('<III', f.read(4*3))

	return FileDescriptor(name, size, padded_size, offset)

def extract_file(f, fd, dest):
	f.seek(fd.offset)
	shutil.copyfileobj(f, dest, fd.size)

@click.command()
@click.argument('FILE', type=click.File('rb'))
@click.option('--extractdir', type=click.Path(), default='unpak')
def cli(file, extractdir):
	extractdir = Path(extractdir)

	# header
	magic, nfiles = struct.unpack('<II', file.read(4*2))
	print(hex(magic))
	assert magic == 0x1dfc8000
	
	# padding
	pad = file.read(0x38)
	assert all(b == 0 for b in pad)

	# file descriptors
	print(nfiles)
	# print(read_fixed_str(file, 0x34))
	files = [read_descriptor(file)
		for _ in range(nfiles)]

	with Progress() as p:
		task = p.add_task('[cyan]unpacking...', total=nfiles)
		for fd in files:
			p.update(task, description=f'[cyan]unpacking[/] {fd.name}[cyan]...', advance=1)

			path = extractdir / Path(fd.name)
			path.parent.mkdir(parents=True, exist_ok=True) # ensure

			with open(path, 'wb') as dest:
				extract_file(file, fd, dest)


if __name__ == '__main__':
	cli()	