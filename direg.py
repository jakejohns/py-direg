#!/usr/bin/env python
"""
Usage:
    direg.py (-h|--help)
    direg.py [--config=<config>] [-v...] [--log=<log>]

Regulates directories based on configuration file

Options:
    --config=<config>  Path to config [default: ~/.direg.py].
    -v                 verbosity level -v, -vv, -vvv

"""

from docopt import docopt
import logging
import os
import sys
import glob
import humanfriendly


logger = logging.getLogger('direg')

# Default Tests

def max_size(directory):
    try:
        max_size = humanfriendly.parse_size(directory.spec['max_size'])
    except KeyError:
        raise UnregulatableError('No "max_size" configured in specification!')

    return  directory.size > max_size 

def max_count(directory):
    try:
        max_count = int(directory.spec['max_count'])
    except KeyError:
        raise UnregulatableError('No "max_count" configured in specification!')
    except ValueError:
        raise UnregulatableError('"max_count" must be an integer!')
    return len(directory.contents) > max_count


# Default Solutions

def remove_old(directory):
    contents = directory.contents
    while contents:
        if not directory.test():
            break
        os.remove(contents.pop())

def send_email(directory):
    raise Exception('Not Implemented')


default_tests = {
        'max_size' : max_size,
        'max_count' : max_count
        }

default_solutions = {
        'remove_old' : remove_old,
        'send_email' : send_email
        }


class UnregulatableError(Exception):
    pass

class DiregDirectory(object):
    """ Represents a directory
    """

    _tester = None
    _solution = None

    def __init__(self, path, spec):
        self.path = path
        self.spec = spec
        try:
            self.tester = spec.get('test', default_tests['max_size'])
            self.solution = spec.get('solution', default_solutions['remove_old'])
        except (KeyError, TypeError):
            raise UnregulatableError 

    @property
    def tester(self):
        """Test strategy should return tru if action required"""
        return self._tester

    @tester.setter
    def tester(self, value):
        if isinstance(value, str):
            try:
                value = default_tests[value]
            except KeyError:
                logger.error('Invalid test "%s"!', value)
                raise

        if not callable(value):
            logger.error('Test is not callable: %s', value)
            raise TypeError

        logger.debug('Setting "%s" test to "%s"', self.path, value.__name__)
        self._tester = value

    @property
    def solution(self):
        """Solution strategy""" 
        return self._solution

    @solution.setter
    def solution(self, value):
        if isinstance(value, str):
            try:
                value = default_solutions[value]
            except KeyError:
                logger.error('Invalid solution "%s"!', value)
                raise

        if not callable(value):
            logger.error('Solution is not callable: %s', value)
            raise TypeError

        logger.debug('Setting "%s" solution to "%s"', self.path, value.__name__)
        self._solution = value


    @property
    def size(self):
        """Size of the files in the directory"""
        logger.debug('Calculating size: %s', self.path)
        total = 0
        for dirpath, dirnames, filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    @property
    def contents(self):
        """Contents of the directory"""
        return self.get_contents()

    def get_contents(self, reverseOrder = True):
        logger.debug('Getting Contents: %s', self.path)
        return sorted((os.path.join(dirname, filename) for dirname, dirnames,
            filenames in os.walk(self.path) for filename in filenames),
            key=lambda fn: os.stat(fn).st_mtime,
            reverse = reverseOrder)

    def test(self):
        """Invokes the test strategy"""
        logger.debug('Testing %s', self.path)
        return self.tester(self)

    def solve(self):
        """Invokes the solution strategy"""
        logger.debug('Solving %s', self.path)
        return self.solution(self)

    def regulate(self):
        """Regulates the directory"""
        logger.info('Regulating directory: "%s", test:"%s", solution:"%s"',
                self.path,
                self.tester.__name__,
                self.solution.__name__)
        if self.test():
            logger.info('Action Required: %s', self.path)
            self.solve()
        else:
            logger.info('No action required: %s', self.path)


def regulate(directories) :
    logger.debug('Regulating %s directories', len(directories))
    for directory in directories :
        try:
            directory.regulate()
        except UnregulatableError, e:
            logger.error(e.message)


def load(directories):
    tasks = []
    for spec in directories:
        try:
            logger.debug('Processing specification for: %s', spec['path'])
            for path in glob.glob(os.path.expanduser(spec['path'])) :
                if not os.path.isdir(path):
                    logger.error('%s is not a directory',  path)
                    continue
                if not os.access(path, os.R_OK):
                    logger.error('%s is not readable', path)
                    continue
                if not os.access(path, os.W_OK):
                    logger.warning('%s is not writable', path)

                logger.debug('adding %s to tasks', path)
                tasks.append(DiregDirectory(path, spec))
        except KeyError:
            logger.error('Directory specification mission path component')
        except UnregulatableError:
            logger.error('Configuration problem! Skipping "%s"', path)

    return tasks


def config_logger(args):
    lvl = logging.ERROR - (10 * args['-v'])
    logger.setLevel(lvl)
    if args['--log']:
        handle = logging.FileHandler(args['--log'])
    else:
        handle = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handle.setLevel(lvl)
    handle.setFormatter(formatter)
    logger.addHandler(handle)

if __name__ == '__main__':
    args = docopt(__doc__, version='direg v0.0.0')
    config_logger(args)
    config = {}
    try:
        configfile = os.path.expanduser(args['--config'])
        logger.debug('Loading config file: %s', configfile)
        execfile(configfile, config)
        logger.debug('Configuration: %s', config['directories'])
    except IOError:
        logger.critical('Cannot read config: %s', configfile)
        sys.exit("Cannot read configuration file")
    regulate(load(config['directories']))




