# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016-2018 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess

from testtools.matchers import DirExists, FileExists, MatchesRegex, Not

from tests import integration, fixture_setup


class RpathTestCase(integration.TestCase):

    def test_origin_rpath(self):
        self.run_snapcraft('prime', 'rpath-test')

        self.assertThat(os.path.join(self.prime_dir, 'binary'), FileExists())
        self.assertThat(
            os.path.join(self.prime_dir, 'lib', 'libfoo.so'), FileExists())

        # Assert that the $ORIGIN rpath did not result in the library being
        # pulled in twice.
        self.assertThat(
            os.path.join(
                self.prime_dir, os.path.abspath(self.prime_dir).lstrip('/')),
            Not(DirExists()))


class Libc6TestCase(integration.TestCase):

    def test_primed_libc6(self):
        snapcraft_yaml = fixture_setup.SnapcraftYaml(self.path)
        snapcraft_yaml.update_part('test-part', {
            'plugin': 'nil',
            'stage-packages': ['libc6', 'hello']
        })
        self.useFixture(snapcraft_yaml)

        self.run_snapcraft('prime')

        bin_path = os.path.join(self.prime_dir, 'usr', 'bin', 'hello')
        self.assertThat(bin_path, FileExists())

        interpreter = subprocess.check_output([
            self.patchelf_command, '--print-interpreter', bin_path]).decode()
        expected_interpreter = r'^/snap/test-snap/current/lib/.*'
        self.assertThat(interpreter, MatchesRegex(expected_interpreter))
