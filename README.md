py-direg
========

Simple utility for regulating directories (eg. deleting old files when a certain size is reached)

## Usage

    Usage:
        direg.py (-h|--help)
        direg.py [--config=<config>] [-v...] [--log=<log>]

    Regulates directories based on configuration file

    Options:
        --config=<config>  Path to config [default: ~/.direg.py].
        -v                 verbosity level -v, -vv, -vvv

## Example Configuration

```python
directories = [

        {
            'path' : '~/podcasts/program',
            'test': 'max_count',
            'max_count':100
        },

        {
            'path' : '~/podcasts/science/*',
            'test': 'max_size',
            'max_size': '100GB'
        }

    ]
```

## Configuration Options

Configuration should define a list of dictionaries called `directories`. Each
dictionary is a directory specification. The specification must consist of the
following keys:

- `path`: the path to the directory. "~" is expanded to user directory. If
    wildcards are are used, globbing will expand to each path, and the remainder
    of the specification is used for each path. 

- `test`: the test to use. Should be callable. Will be called with the
    `DiregDirectory` object as the single parameter. Can also be a string
    referring to one of the predefined tests. The test should return `True` if
    action needs to be taken (if the solution should be called).

- `solution`: the solution to use. Should be callable. Will be called with the
    `DiregDirectory` object as the single parameter. Can also be a string
    referring to one of the predefined solutions. 

- Additional Parameters: If additional parameters are reqquired by the solution
    or test, they should also be included (eg. `max_size`, `max_count`). The
    entirety of the specification is available ad the `spec` property of the
    `DiregDirectory` object that is created from the specificaiton. 

### Predefined Strategies

There are a few predefined test and solution strategies which can be used by
passing a string as the `test` or `solution` key in the directory specification.
Be sure to also include the required additional parameters as well. 

#### Predefined Tests

##### max_size

The `max_size` test can be used by passing `max_size` as the `test` value and
including a `max_size` key that specifies the maximum size that directory is
allowed to be. The `max_Size` parameter is parsed by
[humanfriendly](https://humanfriendly.readthedocs.org/), so string like "100GB"
should work fine. This test returns true if the directory is larger than the
given size (eg. the solution is triggeres).

##### max_count

The `max_count` test can be used by passing `max_count` as the test value and
including a `max_count` key that specifies the maximum number of files allowed
in the directory. 

##### is_after

The `is_after` test checks if today is after the date provided by the directory
spec key `expiry`. Date should be formatted as 'YYYY-MM-DD HH:MM:SS'. Can also
be a callable. 

##### is_day_of_week

The `is_day_of_week` test checks if the current day of week is specified in the
directory spec `dow` entry. Days are specified as integers 0-6 where 0 is
Monday, and 6 is Sunday. This can be a single integer, a list, or tuple, or a
string of numbers to specify multiple days. 

##### always
The `always` test always returns true, so it always triggers the solution.

##### never
The `never` test always returns false, so it never triggers the solution.

#### Predefined Solutions

##### remove_old

The `remove_old` solution is the default solution, and is used if nothing else
is specified. It can also be explicitly declared by passing `remove_old` as the
`solution` value. It simply removes the oldest file in the directory until the
directory test no longer returns true. Be sure that it is used in conjunction
with an appropriate test. 

##### remove_older_than

The `remove_older_than` solution removes files older than the specified time
delta in the direcry spec `cutoff` key. The `cuttoff` may be a number of seconds
old, or a `datetime.timedelta`.

##### send_email

not implemented yet.







