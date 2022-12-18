#!/usr/bin/env python3
from optparse import OptionParser
from .driver import Wiki, OUTPUT


def run():
	parser = OptionParser()
	options = (
		('-u', '--url', 'url', None),
		('-q', '--query', 'query', None),
		('-l', '--lang', 'lang', 'English'),
		('-p', '--part', 'part', 'all'),
		('-i', '--item', 'item', 'all'),
		('-o', '--output', 'output', 'text'),)
	args = [dict(zip(('flag', 'long', 'dest', 'default'), option)) for option in options]
	for arg in args: parser.add_option(
		arg['flag'], arg['long'], dest=arg['dest'], default=arg['default'])
	options = parser.parse_args()[0]
	if options.output not in (formats := OUTPUT()._fields): 
		return print(f"Available output formats: {formats}.")
	output = Wiki(lang=options.lang).search(
	    url=options.url, query=options.query, part=options.part, item=options.item)
	print(getattr(output, options.output))

if __name__ == '__main__': run()
