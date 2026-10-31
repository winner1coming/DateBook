#!/bin/sh
# Pure JVM tests only. Does not install/accept Android SDK or claim device coverage.
set -eu
DATEBOOK_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DATEBOOK_OUT="$DATEBOOK_ROOT/host-test-results"
DATEBOOK_DEPS="${DATEBOOK_TEST_DEPS:-$DATEBOOK_OUT/deps}"
DATEBOOK_KOTLINC="${KOTLINC:-$(command -v kotlinc || true)}"
if [ -z "$DATEBOOK_KOTLINC" ]; then
 echo '需要 Kotlin 2.2.10 CLI 和 JDK17+，或在 Android Studio 配置 SDK 后运行 ./gradlew :core:test :app:testDebugUnitTest。' >&2
 exit 2
fi
DATEBOOK_KOTLIN_LIB="${KOTLIN_LIB:-$(CDPATH= cd -- "$(dirname -- "$DATEBOOK_KOTLINC")/../lib" && pwd)}"
mkdir -p "$DATEBOOK_OUT" "$DATEBOOK_DEPS"
download() {
 if [ ! -f "$DATEBOOK_DEPS/$1.jar" ]; then curl -fL --retry 2 "https://repo.maven.apache.org/maven2/$2" -o "$DATEBOOK_DEPS/$1.jar"; fi
}
download coroutines org/jetbrains/kotlinx/kotlinx-coroutines-core-jvm/1.10.2/kotlinx-coroutines-core-jvm-1.10.2.jar
download serialization-core org/jetbrains/kotlinx/kotlinx-serialization-core-jvm/1.9.0/kotlinx-serialization-core-jvm-1.9.0.jar
download serialization-json org/jetbrains/kotlinx/kotlinx-serialization-json-jvm/1.9.0/kotlinx-serialization-json-jvm-1.9.0.jar
download lunar cn/6tail/lunar/1.7.7/lunar-1.7.7.jar
download junit junit/junit/4.13.2/junit-4.13.2.jar
download hamcrest org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar
DATEBOOK_CP="$DATEBOOK_DEPS/coroutines.jar:$DATEBOOK_DEPS/serialization-core.jar:$DATEBOOK_DEPS/serialization-json.jar:$DATEBOOK_DEPS/lunar.jar:$DATEBOOK_DEPS/junit.jar:$DATEBOOK_DEPS/hamcrest.jar"
"$DATEBOOK_KOTLINC" -jvm-target 17 -Xplugin="$DATEBOOK_KOTLIN_LIB/kotlinx-serialization-compiler-plugin.jar" -classpath "$DATEBOOK_CP" \
 "$DATEBOOK_ROOT"/core/src/main/kotlin/cn/datebook/core/*.kt \
 "$DATEBOOK_ROOT"/core/src/test/kotlin/cn/datebook/core/*.kt \
 "$DATEBOOK_ROOT/app/src/main/kotlin/cn/datebook/app/LunarAdapter.kt" \
 "$DATEBOOK_ROOT/app/src/test/kotlin/cn/datebook/app/LunarGoldenTests.kt" \
 -d "$DATEBOOK_OUT/host-tests.jar"
if [ -n "${JAVA_HOME:-}" ]; then DATEBOOK_JAVA="$JAVA_HOME/bin/java"; else DATEBOOK_JAVA=java; fi
"$DATEBOOK_JAVA" -cp "$DATEBOOK_OUT/host-tests.jar:$DATEBOOK_CP:$DATEBOOK_KOTLIN_LIB/kotlin-stdlib.jar" org.junit.runner.JUnitCore \
 cn.datebook.core.CoreTests cn.datebook.core.FileCodecTests cn.datebook.app.LunarGoldenTests
