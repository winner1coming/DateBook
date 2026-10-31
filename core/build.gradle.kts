plugins { alias(libs.plugins.kotlin.jvm); alias(libs.plugins.kotlin.serialization) }
kotlin { jvmToolchain(17) }
dependencies {
 implementation(libs.coroutines.core)
 implementation(libs.serialization.json)
 implementation(libs.lunar)
 testImplementation(libs.junit)
}
