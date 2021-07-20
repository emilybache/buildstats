from io import StringIO

import pytest
from approvaltests import verify

from process_stats import *
from buildstats import Build
from process_stats import total_build_count_excluding_clean

SAMPLE_BUILDS = [
        Build(when='2021-07-16 13:58:29,316', time_taken='35 s 559 ms ', outcome='finished',
              tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources'),
        Build(when='2021-07-15 16:37:12,979', time_taken='3 m 28 s 451 ms ', outcome='finished', tasks='clean'),
        Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble'),
        Build(when='2021-07-16 13:33:31,933', time_taken='2 m 17 s 252 ms ', outcome='finished', tasks=':app:assemble'),
    ]


def test_total_time():
    assert total_time(SAMPLE_BUILDS) == pytest.approx(523.69, 0.1)
    assert total_time_excluding_clean(SAMPLE_BUILDS) == pytest.approx(315.239, 0.1)


def test_total_build_count():
    assert total_build_count_excluding_clean(SAMPLE_BUILDS) == 3
    assert total_build_count(SAMPLE_BUILDS) == 4


def test_median_build_time():
    assert median_build_time(SAMPLE_BUILDS) == pytest.approx(139.84, 0.1)
    assert median_build_time_excluding_clean(SAMPLE_BUILDS) == pytest.approx(137.252, 0.1)


def test_deduplicate():
    builds = SAMPLE_BUILDS[:] + [Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble')]
    assert len(deduplicate(builds)) == len(SAMPLE_BUILDS)


def test_gather_builds_from():
    file_contents = """\
Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')
Build(when='2021-07-15 16:59:35,922', time_taken='3 m 13 s 646 ms ', outcome='finished', tasks=':app:assembleAcmeEuDebug')
Build(when='2021-07-16 14:05:23,407', time_taken='31 s 669 ms ', outcome='finished', tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources')
"""
    builds = gather_builds_from(StringIO(file_contents))
    assert len(builds) == 3
    assert builds[0] == Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')


def test_gather_builds_from_with_junk():
    file_contents = """\
Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')
syntax_error
Build(when='2021-07-16 14:05:23,407', time_taken='31 s 669 ms ', outcome='finished', tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources')
"""
    builds = gather_builds_from(StringIO(file_contents))
    assert len(builds) == 2
    assert builds[0] == Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')


def test_gather_builds():
    folder = "data"
    output = StringIO()
    gather_builds(folder, output)
    verify(output.getvalue())