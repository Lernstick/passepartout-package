from argparse import ArgumentParser, FileType
from copy import deepcopy
import logging
import os

import yaml

from passepartout.builder import PassepartoutPackageBuilder

def passepartout_package():

    parser = ArgumentParser(description='Build a Debian package from a Passepartout DVD source tree.')
    parser.add_argument('config', type=FileType('r'),
                        help='YAML file describing package source and metadata.')
    parser.add_argument('packages', action='store', nargs="*",
                        help='Package to build. Package metadata must be defined in config.')
    parser.add_argument('-d', '--distribution', default='lernstick-8',
                        help='Target distribution for the package')
    parser.add_argument('-b', '--builddir', default='build',
                        help='Directory used for building the package. '
                             'This directory will also contain the built packages.')
    parser.add_argument('--basedir', default=None,
                        help='Base directory for paths in the config file. Defaults to the '
                             'directory of the config file.')
    parser.add_argument('-v', '--verbose', action='store_const', const=logging.INFO,
                        default=logging.WARN,
                        help='Enable verbose output.')
    parser.add_argument('--debug', action='store_const', const=logging.DEBUG,
                        default=logging.WARN,
                        help='Enable debugging output.')
    args = parser.parse_args()

    config = yaml.load(args.config.read())

    if not args.packages:
        args.packages = [ k for k in config.keys() if not k.startswith('default-') and k != 'default' ]

    if not args.basedir:
        args.basedir = os.path.dirname(os.path.abspath(args.config.name))

    logging.basicConfig(format='%(message)s', level=min(args.verbose, args.debug))
    for package in args.packages:
        logging.info("Starting build of package '%s'" % package)
        try:
            package_config = deepcopy(config[package])
            package_config['name'] = package
            builder = PassepartoutPackageBuilder(package_config, args.distribution, args.builddir, args.basedir)
            builder.build()
        except:
            logging.error("Failed to build package '%s'." % package)
            raise

        logging.info("Finished build of package '%s'" % package)
