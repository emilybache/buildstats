from io import StringIO

from approvaltests import verify

from process_to_csv import *
from gather_build_data import Build, Sync


SAMPLE_BUILDS = [
    Build(when='2021-07-16 13:58:29,316', time_taken='35 s 559 ms ', outcome='finished',
          tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources'),
    Build(when='2021-07-16 16:37:12,979', time_taken='3 m 28 s 451 ms ', outcome='finished', tasks='clean'),
    Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble'),
    Build(when='2021-07-16 13:33:31,933', time_taken='2 m 17 s 252 ms ', outcome='finished', tasks=':app:assemble'),
]

SAMPLE_BUILDS_2 = [
    Build(when='2021-07-15 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished',
          tasks=':app:assembleAcmeEuDebug'),
    Build(when='2021-07-15 13:33:31,933', time_taken='2 m 17 s 252 ms ', outcome='finished',
          tasks=':app:assembleAcmeEuDebug'),
]

SAMPLE_BUILDS_3 = [
    Sync(when='2021-07-13 13:51:14,719', time_taken='4 m 39 s 614 ms ', outcome='finished',
         project='mobileapp-android'),
    Sync(when='2021-07-13 14:20:08,740', time_taken='4 m 22 s 777 ms ', outcome='finished',
         project='mobileapp-android'),
]


def test_deduplicate():
    builds = SAMPLE_BUILDS[:] + [
        Build(when='2021-07-16 12:31:45,195', time_taken='2 m 22 s 428 ms ', outcome='finished', tasks=':app:assemble')]
    assert len(deduplicate(builds)) == len(SAMPLE_BUILDS)


def test_gather_builds_from():
    file_contents = """\
Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')
Build(when='2021-07-15 16:59:35,922', time_taken='3 m 13 s 646 ms ', outcome='finished', tasks=':app:assembleAcmeEuDebug')
Build(when='2021-07-16 14:05:23,407', time_taken='31 s 669 ms ', outcome='finished', tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources')
"""
    builds = gather_builds_from(StringIO(file_contents))
    assert len(builds) == 3
    assert builds[0] == Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished',
                              tasks='clean')


def test_gather_builds_from_with_junk():
    file_contents = """\
Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished', tasks='clean')
syntax_error
Build(when='2021-07-16 14:05:23,407', time_taken='31 s 669 ms ', outcome='finished', tasks=':gmode:generateAcmeEuDebugSources, :gmode:createMockableJar, :gmode:generateAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugUnitTestSources, :gmode:compileAcmeEuDebugAndroidTestSources, :gmode:compileAcmeEuDebugSources')
"""
    builds = gather_builds_from(StringIO(file_contents))
    assert len(builds) == 2
    assert builds[0] == Build(when='2021-07-15 16:54:09,703', time_taken='55 s 836 ms ', outcome='finished',
                              tasks='clean')


def test_gather_builds(tmpdir):
    # Write some sample builds to two different log files in a temporary directory
    folder = tmpdir
    filename1 = folder / "2021-07-15-sample.log"
    with open(filename1, "w") as f1:
        for build in SAMPLE_BUILDS_2:
            f1.write(f"{build}\n")
    filename2 = folder / "2021-07-16-sample.log"
    with open(filename2, "w") as f2:
        for build in SAMPLE_BUILDS:
            f2.write(f"{build}\n")

    # gather builds into an in-memory file-like object
    output = StringIO()
    gather_builds(folder, output)

    # use Approvals to verify that the builds were gathered correctly
    verify(output.getvalue())


