from copy import deepcopy
import os
import shutil
from subprocess import check_call, DEVNULL
import tarfile

from jinja2 import Environment, PackageLoader

class PassepartoutPackageBuilderException(Exception):
    pass

class InvalidSource(PassepartoutPackageBuilderException):
    pass

class PassepartoutPackageBuilder(object):

    def __init__(self, package, distribution='lernstick-8', builddir='build', basedir='sources'):
        # initialize Jinja2 template environment
        self._template_env = Environment(loader=PackageLoader('passepartout', 'templates'))

        self.package = package

        # expand templates in package configuration
        for i in self.package['menuitems']:
            values = deepcopy(self.package)
            values.update(i)
            self._expand_templates(i, values)
        self._expand_templates(self.package, self.package)

        # set variables
        self.distribution = distribution
        self.basedir = basedir
        self.builddir = builddir

    def build(self):
        self._unpack()
        self._populate_debian()
        self._build_package()

    def _unpack(self):
        source_tarname = os.path.join(self.basedir, self.package['source'])
        source_ext = os.path.splitext(source_tarname)[1]
        tar = tarfile.open(source_tarname)
        tar.extractall(path=self.builddir)
        basedir = os.path.join(self.builddir, os.path.commonprefix(tar.getnames()))
        if basedir == self.builddir or not os.path.isdir(basedir):
            raise InvalidSource('Source tarfile must contain a common base directory.')

        os.rename(basedir, os.path.join(self.builddir, self.package['name']))

        orig_tarname = '%s_%s.orig.tar%s' % (self.package['name'],
                                             self.package['upstream_version'],
                                             source_ext)

        dst = os.path.join(self.builddir, orig_tarname)
        if os.path.lexists(dst):
            os.remove(dst)
        os.symlink(source_tarname, dst)

    def _populate_debian(self):

        debian_dir = os.path.join(self.builddir, self.package['name'], 'debian')
        if os.path.exists(debian_dir):
            shutil.rmtree(debian_dir)
        os.mkdir(debian_dir)
        os.mkdir('%s/source' % debian_dir)

        # Create control file
        self._write_template(os.path.join(debian_dir, 'control'), 'control')

        # Create rules file
        self._write_template(os.path.join(debian_dir, 'rules'), 'rules')

        # Create changelog
        curdir = os.getcwd()
        try:
            os.chdir(os.path.join(self.builddir, self.package['name']))
            check_call(['dch',
                        '-v',
                        '%s-%s' % (self.package['upstream_version'], self.package['debian_version']),
                        '--create',
                        '-D',
                        self.distribution,
                        '--force-distribution',
                        '--package',
                        self.package['name'],
                        'This package ws created with passepartout-package',
                        ],
                       stdin=DEVNULL, stdout=DEVNULL)

        finally:
            os.chdir(curdir)

        # Create menu entries
        for i, entry in enumerate(self.package['menuitems']):
            self._write_template(os.path.join(debian_dir,
                                              '%s-%s.desktop' % (self.package['name'], i+1)),
                                 'menu.desktop',
                                 title=entry['title'],
                                 directory=entry['directory'],
                                 start_page=entry['start_page'],
                                 )

        # create menu directory
        if self.package['menu_directory']:
            self._write_template(os.path.join(debian_dir,
                                              '%s.directory' % self.package['name']),
                                 'menu.directory')

            # create menu merge configuration
            self._write_template(os.path.join(debian_dir,
                                              '%s.merge.menu' % self.package['name']),
                                 'merge.menu')

        # source package and debhelper files
        self._write_template(os.path.join(debian_dir, 'compat'), 'compat')
        self._write_template(os.path.join(debian_dir, 'source/format'), 'source/format')
        self._write_template(os.path.join(debian_dir, 'source/options'), 'source/options')
        self._write_template(os.path.join(debian_dir, 'source/include-binaries'),
                             'source/include-binaries')

        if self.package['icon']:
            shutil.copy(os.path.join(self.basedir, self.package['icon']),
                        os.path.join(debian_dir, '%s.png' % self.package['name']))

    def _build_package(self):

        # Build package
        curdir = os.getcwd()
        builddir = os.path.join(self.builddir, self.package['name'])
        try:
            os.chdir(builddir)
            check_call(['dpkg-buildpackage',
                        '-rfakeroot',
                        '-uc',
                        '-us',
                        ],
                       stdin=DEVNULL, stdout=DEVNULL)
        finally:
            os.chdir(curdir)

        # remove source tree
        shutil.rmtree(builddir)

    def _write_template(self, fname, template, **kwargs):
        template = self._template_env.get_template(template)
        open(fname, 'w').write(template.render(self.package, **kwargs))

    def _expand_templates(self, templates, values):

        for k, v in templates.items():
            if not isinstance(v, str):
                # only strings can be templates
                continue

            t = self._template_env.from_string(v)
            templates[k] = t.render(values)
