// CI-only Gradle init script applied when building the integration sample
// against the Kotlin 1.9 SDK variant (`-k19`).
//
// Workaround for a known SDK publishing issue: the `-k19` aggregate POM does
// not currently propagate strict version constraints on `kotlin-stdlib` /
// `kotlinx-coroutines`, so transitive AndroidX dependencies pull artifacts
// compiled with K2.1 metadata, which the 1.9.25 compiler cannot read:
//
//   e: Module was compiled with an incompatible version of Kotlin.
//   The binary version of its metadata is 2.1.0, expected version is 1.9.0.
//
// Forced versions match what the `-k19` SDK is itself built against (see
// `versions/build.gradle.kts`: `kotlin = 2.0.21`, `coroutines = 1.9.0`).
//
// Follow-up: once the `-k19` aggregate POM emits the proper strict
// constraints (as the released `100.6.0-k19` does), this file and the
// `--init-script` flag in `.gitlab/ci/deploy.yml` can be removed.
allprojects {
    configurations.all {
        resolutionStrategy {
            force(
                "org.jetbrains.kotlin:kotlin-stdlib:2.0.21",
                "org.jetbrains.kotlin:kotlin-stdlib-jdk7:2.0.21",
                "org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.0.21",
                "org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0",
                "org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0",
                "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0",
            )
        }
    }
}
