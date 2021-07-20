import datetime
from io import StringIO

import buildstats
from buildstats import filter_gradle_builds, Build, output_filename


def test_filter_gradle_builds():
    text = """\
2021-07-14 15:08:52,831 [ 678061]   INFO - g.FileBasedIndexProjectHandler - Reindexing refreshed files: 0 to update, calculated in 0ms 
2021-07-14 15:20:21,542 [1366772]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 16 m 5 s 163 ms 
    at com.intellij.openapi.application.impl.ApplicationImpl.runIntendedWriteActionOnCurrentThread(ApplicationImpl.java:808)
"""
    builds = filter_gradle_builds(StringIO(text))

    assert list(builds) == [
        Build(when="2021-07-14 15:20:21,542", time_taken="16 m 5 s 163 ms ", outcome="finished",
              tasks="")]


def test_build_matcher():
    line = "2021-07-14 15:20:21,542 [1366772]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 16 m 5 s 163 ms\n"
    matches = buildstats.GRADLE_BUILD_RE.match(line)
    assert matches.group(1) == "2021-07-14 15:20:21,542"
    assert matches.group(2) == "finished"
    assert matches.group(3) == "16 m 5 s 163 ms"


def test_task_matcher():
    line = "2021-07-14 16:50:59,433 [6804663]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [clean]\n"
    matches = buildstats.GRADLE_TASKS_RE.match(line)
    assert matches.group(1) == "clean"


def test_task_matcher_multiple_tasks():
    line = "2021-07-14 16:50:59,433 [6804663]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [:assemble-xyz, :testClasses]\n"
    matches = buildstats.GRADLE_TASKS_RE.match(line)
    assert matches.group(1) == ":assemble-xyz, :testClasses"


def test_next_match():
    text = """\
2021-07-14 16:50:59,433 [6804663]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [clean] 
2021-07-14 16:50:59,667 [6804897]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 214 ms
"""
    matches = buildstats.next_match(StringIO(text),
                                    [buildstats.NamedRegex(buildstats.GRADLE_BUILD_RE, "build"),
                                     buildstats.NamedRegex(buildstats.GRADLE_TASKS_RE, "tasks")]
                                    )
    assert matches.__next__()[0] == "tasks"
    assert matches.__next__()[0] == "build"


def test_filter_clean_builds():
    text = """\
2021-07-14 16:50:59,433 [6804663]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [clean] 
2021-07-14 16:50:59,439 [6804669]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [clean] 
2021-07-14 16:50:59,441 [6804671]   INFO - s.plugins.gradle.GradleManager - Instructing gradle to use java from /Users/emilybache/Library/Application Support/JetBrains/Toolbox/apps/AndroidStudio/ch-0/202.7486908/Android Studio.app/Contents/jre/jdk/Contents/Home 
2021-07-14 16:50:59,451 [6804681]   INFO - ild.invoker.GradleBuildInvoker - Build command line options: [-Pandroid.injected.invoked.from.ide=true, -Pandroid.injected.studio.version=202.7660.26.42.7486908, -Pandroid.injected.attribution.file.location=/Users/emilybache/workspace/app/buildSrc/.gradle] 
2021-07-14 16:50:59,452 [6804682]   INFO - xecution.GradleExecutionHelper - Passing command-line args to Gradle Tooling API: -Pandroid.injected.invoked.from.ide=true -Pandroid.injected.studio.version=202.7660.26.42.7486908 -Pandroid.injected.attribution.file.location=/Users/emilybache/workspace/app/buildSrc/.gradle 
2021-07-14 16:50:59,646 [6804876]   INFO - s.plugins.gradle.GradleManager - Instructing gradle to use java from /Users/emilybache/Library/Application Support/JetBrains/Toolbox/apps/AndroidStudio/ch-0/202.7486908/Android Studio.app/Contents/jre/jdk/Contents/Home 
2021-07-14 16:50:59,650 [6804880]   INFO - ild.invoker.GradleBuildInvoker - Build command line options: [-Pandroid.injected.invoked.from.ide=true, -Pandroid.injected.studio.version=202.7660.26.42.7486908, -Pandroid.injected.attribution.file.location=/Users/emilybache/workspace/app/.gradle] 
2021-07-14 16:50:59,651 [6804881]   INFO - xecution.GradleExecutionHelper - Passing command-line args to Gradle Tooling API: -Pandroid.injected.invoked.from.ide=true -Pandroid.injected.studio.version=202.7660.26.42.7486908 -Pandroid.injected.attribution.file.location=/Users/emilybache/workspace/app/.gradle 
2021-07-14 16:50:59,667 [6804897]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 214 ms 
"""
    builds = filter_gradle_builds(StringIO(text))

    assert list(builds) == [
        Build(when="2021-07-14 16:50:59,667", time_taken="214 ms ", outcome="finished", tasks="clean")]


def test_parse():
    assert Build(when="2021-07-14 16:50:59,667", time_taken="214 ms ", outcome="finished", tasks="clean") == eval(
        """Build(when="2021-07-14 16:50:59,667", time_taken="214 ms ", outcome="finished", tasks="clean")""")


def test_filename():
    d = datetime.date(2021, 7, 15)
    assert "2021-07-15-emily.log" == output_filename(user="emily", date=d)


def test_output_to_file():
    text = """\
2021-07-14 15:08:52,831 [ 678061]   INFO - g.FileBasedIndexProjectHandler - Reindexing refreshed files: 0 to update, calculated in 0ms 
2021-07-14 15:20:21,542 [1366772]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 16 m 5 s 163 ms 
        at com.intellij.openapi.application.impl.ApplicationImpl.runIntendedWriteActionOnCurrentThread(ApplicationImpl.java:808)
    """
    output = StringIO()
    buildstats.parse_builds(StringIO(text), output)
    assert output.getvalue() == f"""{Build(when="2021-07-14 15:20:21,542", time_taken="16 m 5 s 163 ms ", outcome="finished", tasks="")}\n"""

def test_to_csv():
    build = Build(when='2021-07-15 16:37:12,979', time_taken='3 m 28 s 451 ms ', outcome='finished', tasks='clean')
    assert str(build.to_csv()) == """2021-07-15 16:37:12,979, 208.451, finished, clean"""

def test_parse_to_secs():
    assert buildstats.parse_to_secs('252 ms ') == 0.252
    assert buildstats.parse_to_secs('17 s 252 ms ') == 17.252
    assert buildstats.parse_to_secs('2 m 17 s 252 ms ') == 137.252
