plugins {
 alias(libs.plugins.android.application)
 alias(libs.plugins.kotlin.compose)
 alias(libs.plugins.kotlin.serialization)
 alias(libs.plugins.ksp)
 alias(libs.plugins.room)
}
android {
 namespace = "cn.datebook.app"
 compileSdk = 37
 defaultConfig {
  applicationId = "cn.datebook.app"
  minSdk = 26
  targetSdk = 37
  versionCode = 1
  versionName = "1.0.0"
  testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
 }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
 buildFeatures { compose = true; buildConfig = true }
 buildTypes { release { isMinifyEnabled = true; proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro") } }
 packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}
room { schemaDirectory("$projectDir/schemas") }
dependencies {
 implementation(project(":core"))
 implementation(platform(libs.compose.bom))
 implementation(libs.compose.ui); implementation(libs.compose.preview); implementation(libs.compose.material3); implementation(libs.compose.icons)
 implementation(libs.activity); implementation(libs.lifecycle.runtime); implementation(libs.lifecycle.viewmodel); implementation(libs.navigation)
 implementation(libs.room.runtime); implementation(libs.room.ktx); ksp(libs.room.compiler)
 implementation(libs.coroutines.android); implementation(libs.serialization.json); implementation(libs.datastore)
 implementation(libs.work); implementation(libs.glance); implementation(libs.biometric); implementation(libs.lunar)
 implementation("androidx.core:core-ktx:1.16.0")
 debugImplementation(libs.compose.tooling)
 testImplementation(libs.junit)
 androidTestImplementation("androidx.test.ext:junit:1.2.1")
 androidTestImplementation("androidx.test:runner:1.6.2")
 androidTestImplementation("androidx.room:room-testing:2.8.5")
 androidTestImplementation(platform(libs.compose.bom))
 androidTestImplementation("androidx.compose.ui:ui-test-junit4")
 debugImplementation("androidx.compose.ui:ui-test-manifest")
}
