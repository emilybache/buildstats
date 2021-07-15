from io import StringIO

import buildstats
from buildstats import filter_gradle_builds, Build


def test_filter_gradle_builds():
    text = """\
2021-07-14 15:04:16,263 [ 401493]   INFO - ild.invoker.GradleBuildInvoker - About to execute Gradle tasks: [:assemble, :testClasses] 
2021-07-14 15:08:52,831 [ 678061]   INFO - g.FileBasedIndexProjectHandler - Reindexing refreshed files: 0 to update, calculated in 0ms 
2021-07-14 15:20:21,542 [1366772]   INFO - ild.invoker.GradleBuildInvoker - Gradle build finished in 16 m 5 s 163 ms 
    at com.intellij.openapi.application.impl.ApplicationImpl.runIntendedWriteActionOnCurrentThread(ApplicationImpl.java:808)
"""
    builds = filter_gradle_builds(StringIO(text))

    assert list(builds) == [
        Build(when="2021-07-14 15:20:21,542", time_taken="16 m 5 s 163 ms ", outcome="finished",
              tasks=":assemble, :testClasses")]


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


def test_task_list():
    assert buildstats.task_list("clean") == ["clean"]
    assert buildstats.task_list("") == []
    assert buildstats.task_list((":assemble, :testClasses")) == [":assemble", ":testClasses"]


def test_parse():
    assert Build(when="2021-07-14 16:50:59,667", time_taken="214 ms ", outcome="finished", tasks="clean") == eval(
        """Build(when="2021-07-14 16:50:59,667", time_taken="214 ms ", outcome="finished", tasks="clean")""")
