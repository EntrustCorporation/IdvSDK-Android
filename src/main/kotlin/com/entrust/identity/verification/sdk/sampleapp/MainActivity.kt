package com.entrust.identity.verification.sdk.sampleapp

import android.app.AlertDialog
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import com.entrust.identity.verification.sdk.api.ClassicParameters
import com.entrust.identity.verification.sdk.api.Configuration
import com.entrust.identity.verification.sdk.api.EntrustIDV
import com.entrust.identity.verification.sdk.api.Localisation
import com.entrust.identity.verification.sdk.api.StudioParameters
import com.entrust.identity.verification.sdk.api.callbacks.BiometricsTokenHandler
import com.entrust.identity.verification.sdk.api.callbacks.Callbacks
import com.entrust.identity.verification.sdk.api.steps.FaceMotion
import com.entrust.identity.verification.sdk.api.steps.FacePhoto
import com.entrust.identity.verification.sdk.api.steps.Welcome
import com.entrust.identity.verification.sdk.api.theming.Branding
import com.entrust.identity.verification.sdk.api.theming.ColorTokens
import com.entrust.identity.verification.sdk.api.theming.Theme
import com.entrust.identity.verification.sdk.api.theming.ThemeMode

class MainActivity : AppCompatActivity() {

    // Create a SDK token for this applicant in your backend and use it here
    private val sdkToken = "YOUR_SDK_TOKEN"

    // For Studio flows, create a Studio-type SDK token for this applicant instead (in your backend) and use it here
    // Workflow Run ID is required for Studio-type SDK tokens and it's embedded in the studio token
    private val studioToken = "YOUR_STUDIO_TOKEN"

    private val classicSteps = listOf(
        Welcome(),
        FacePhoto(options = FacePhoto.Options(showIntro = false)),
        FaceMotion(options = FaceMotion.Options(showIntro = false)),
    )

    // Language keys: https://sdk.onfido.com/capture/i18n/index.json
    // Custom translations for a module name and a language: https://sdk.onfido.com/capture/i18n/welcome/en_US.min.json
    // Commons translations for a language: https://sdk.onfido.com/capture/i18n/common/en_US.min.json
    val customTranslations = Localisation(
        language = "en_US",
        allowedLanguages = listOf("en_US"),
        overrides = mapOf(
            "en_US" to mapOf(
                "welcome.title" to "Custom welcome title",
                "welcome.button.default" to "Custom button text",
            ),
        ),
    )

    val customThemeComingSoon = Theme(
        mode = ThemeMode.Light,
        branding = Branding(
            text = "Brand Name",
            logo = "https://upload.wikimedia.org/wikipedia/commons/d/d7/Android_robot.svg",
        ),
        lightColors = mapOf(
            ColorTokens.BackgroundColorOverlay to "#10598A85", // pass RGBA HEX colors, we internally convert to ARGB
        ),
        darkColors = mapOf(
            ColorTokens.BackgroundColorOverlay to "#10598A85", // pass RGBA HEX colors, we internally convert to ARGB
        ),
    )

    @Suppress("UnusedPrivateProperty")
    private val classicFlowParameters = ClassicParameters(
        sdkToken = sdkToken,
        steps = classicSteps,
        configuration = Configuration(
            disableAnalytics = false,
            theme = customThemeComingSoon,
            localisation = customTranslations,
        ),
    )


    private val studioFlowParameters = StudioParameters(
        sdkToken = studioToken,
        configuration = Configuration(
            disableAnalytics = false,
            theme = customThemeComingSoon,
            localisation = customTranslations,
        ),
    )

    private val sdk = EntrustIDV(
        activity = this,
        callbacks = Callbacks(
            onComplete = { result ->
                Log.d("MainActivity", "The onComplete callback has been called. Received: $result")
                finish()
            },
            onError = {
                Log.e("MainActivity", "The onError callback has been called with: $it")
                AlertDialog
                    .Builder(this@MainActivity)
                    .setTitle("An error occurred")
                    .setMessage(it.message)
                    .setPositiveButton("Ok") { dialog, _ ->
                        dialog.dismiss()
                        finish()
                    }.show()
            },
            onUserExit = {
                Log.d("MainActivity", "The onUserExit has been called with: userAction: $it")
                finish()
            },
        ),
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        sdk.start(studioFlowParameters) // For classic flows, use: sdk.start(classicFlowParameters) instead
    }
}