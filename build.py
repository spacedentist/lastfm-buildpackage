#!/usr/bin/env python

import errno
import os
import shutil
import subprocess
import sys

packages = {
    'liblastfm': {
        'version': '1.0.6',
        'sources': 'https://github.com/lastfm/liblastfm/archive/{version}.tar.gz',
        },
    'lastfm-desktop': {
        'version': '2.1.33',
        'sources': 'https://github.com/lastfm/lastfm-desktop/archive/{version}.tar.gz',
        },
    }

def main():
    project, distribution = sys.argv[1:]
    info = packages[project]
    version = info['version']
    source_url = info['sources'].format(version=version)

    assert os.path.isdir('{0}/debian-{1}'.format(project, distribution))

    try:
        os.mkdir('{0}/build'.format(project, distribution))
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise

    builddir = '{0}/build/{1}'.format(project, distribution)
    try:
        shutil.rmtree(builddir)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise
    os.mkdir(builddir)

    tgz = '{0}/build/{0}_{1}.orig.tar.gz'.format(project, version)
    if not os.path.exists(tgz):
        subprocess.call(['wget', '-O', tgz, source_url.format(**info)])

    subprocess.call(['tar', 'vxz'], stdin=open(tgz, 'rb'), cwd=builddir)
    sourcedir = '{0}/{1}-{2}'.format(builddir, project, version)
    assert os.path.isdir(sourcedir)

    shutil.copytree('{0}/debian-{1}'.format(project, distribution), '{0}/debian'.format(sourcedir))
    os.link(tgz, os.path.join(builddir, os.path.basename(tgz)))

    subprocess.call(
        ['dpkg-buildpackage', '-S', '-sa', '--changes-option=-DDistribution='+distribution],
        cwd = sourcedir,
        )


if __name__ == '__main__':
    main()
