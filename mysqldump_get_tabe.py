#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''
Вытаскивание описания и данных указанных таблиц из дампа MySql

Copyright (C) 2011  Alexandr N. Zamaraev (aka tonal)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import gzip
import logging
from optparse import OptionParser
import os.path as osp
import sys

START_TABLE_STRUCT = '%s Table structure for table '

def main(opts):
  if not opts.tables:
    return
  parse = start_parse
  if opts.start_comm == 'auto':
    parse = start_comm_parse
  else:
    parse = start_parse
    init_comm(opts.start_comm)
  tables = set(opts.tables)
  ofile = opts.ofile
  for line in opts.ifile:
    parse = parse(line, ofile, tables)
    if not parse:
      return

def init_comm(comm):
  global START_TABLE_STRUCT
  START_TABLE_STRUCT = START_TABLE_STRUCT % comm

def start_comm_parse(line, ofile, tables):
  if line.startswith('#'):
    init_comm('#')
  elif line.startswith('--'):
    init_comm('--')
  else:
    sys.exit('Do not recognized comment for table struct')
  return start_parse(line, ofile, tables)

def start_parse(line, ofile, tables):
  if not line.startswith(START_TABLE_STRUCT):
    return start_parse
  tbl = line.split('`')[1].lower()
  if tbl not in tables:
    return start_parse
  tables.remove(tbl)
  print>>ofile, line.rstrip()
  return copy_table

def copy_table(line, ofile, tables):
  if not line.startswith(START_TABLE_STRUCT):
    print>>ofile, line.rstrip()
    return copy_table
  if not tables:
    return None
  return start_parse(line, ofile, tables)

def __parse_opt():
  parser = OptionParser(usage='usage: %prog [options]')
  parser.add_option(
    "-t", "--tables", dest="tables",
    help="tables for extract (split comma) ")
  parser.add_option(
    "-i", "--input", dest="ifile", default="stdin",
    help="input file FILE [default: %default]", metavar="FILE")
  parser.add_option(
    "-o", "--output", dest="ofile", default="stdout",
    help="output file FILE [default: %default]", metavar="FILE")
  parser.add_option(
    "-l", "--log", dest="log", default="",
    help="log file FILE [default: %default]", metavar="FILE")
  parser.add_option(
    "-c", "--start-comment", dest="start_comm", default='auto',
    help="start comment for table struct (--|#|auto) [default: %default]")
  parser.add_option(
    "-g", "--gzip", action="store_true", dest="gzip", default=False,
    help="input gzipped")
  parser.add_option(
    "-q", "--quiet", action="store_true", dest="quiet", default=False,
    help="don't print status messages to stdout")
  parser.add_option(
    '-v', '--verbose', action='store_true', dest='verbose', default=False,
    help='print verbose status messages to stdout')
  parser.add_option(
    '', '--version', action='store_true', dest='version', default=False,
    help='print version and license to stdout')
  (opts, args) = parser.parse_args()
  if opts.tables:
    opts.tables = frozenset(
      tbl.strip().lower() for tbl in opts.tables.split(','))
  iname = opts.ifile
  opts.ifile = open(iname) if iname != 'stdin' else sys.stdin
  if opts.gzip:
    opts.ifile = gzip.GzipFile(iname, fileobj=opts.ifile)
  opts.ofile = open(opts.ofile, 'w') if opts.ofile != 'stdout' else sys.stdout
  return opts, args

def print_version():
  print 'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>'

def __init_log(opts):
  u'Настройка лога'
  format = '%(asctime)s %(levelname)-8s %(message)s'
  datefmt = '%Y-%m-%d %H:%M:%S'
  level = logging.DEBUG if opts.verbose else (
    logging.WARNING if opts.quiet else logging.INFO)
  logging.basicConfig(
    level=level,
    format=format, datefmt=datefmt)
  if not opts.log:
    return
  log = logging.FileHandler(opts.log, 'a', 'utf-8')
  log.setLevel(level)
  formatter = logging.Formatter(fmt=format, datefmt=datefmt)
  log.setFormatter(formatter)
  logging.getLogger('').addHandler(log)

if __name__ == '__main__':
  opts, args = __parse_opt()
  if opts.version:
    print_version()
  else:
    __init_log(opts)
    main(opts)
