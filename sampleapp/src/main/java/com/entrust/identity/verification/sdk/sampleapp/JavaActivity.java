package com.entrust.identity.verification.sdk.sampleapp;

import android.os.Bundle;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.entrust.identity.verification.sdk.api.ClassicParameters;
import com.entrust.identity.verification.sdk.api.Configuration;
import com.entrust.identity.verification.sdk.api.EntrustIDV;
import com.entrust.identity.verification.sdk.api.Localisation;
import com.entrust.identity.verification.sdk.api.StudioParameters;
import com.entrust.identity.verification.sdk.api.callbacks.BiometricsTokenHandler;
import com.entrust.identity.verification.sdk.api.callbacks.Callbacks;
import com.entrust.identity.verification.sdk.api.steps.FaceMotion;
import com.entrust.identity.verification.sdk.api.steps.FacePhoto;
import com.entrust.identity.verification.sdk.api.steps.Step;
import com.entrust.identity.verification.sdk.api.steps.StepNames;
import com.entrust.identity.verification.sdk.api.steps.StepOptions;
import com.entrust.identity.verification.sdk.api.steps.Welcome;
import com.entrust.identity.verification.sdk.api.theming.ColorTokens;
import com.entrust.identity.verification.sdk.api.theming.Theme;
import com.entrust.identity.verification.sdk.api.theming.Branding;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import kotlin.coroutines.Continuation;

public class JavaActivity extends AppCompatActivity {

    // Create a SDK token for this applicant in your backend and use it here
    private final String sdkToken = "YOUR_SDK_TOKEN";

    // For Studio flows, create a Studio-type SDK token for this applicant instead (in your backend) and use it here
    // Workflow Run ID is required for Studio-type SDK tokens and it's embedded in the studio token
    private final String studioToken = "YOUR_STUDIO_TOKEN";

    private final List<Step<? extends StepOptions>> classicSteps = Arrays.asList(
        new Welcome(),
        new FacePhoto(
            StepNames.FACE_PHOTO,
            new FacePhoto.Options(false)
        ),
        new FaceMotion(
            StepNames.FACE_MOTION,
            new FaceMotion.Options(false, true)
        )
    );

    // Language keys: https://sdk.onfido.com/capture/i18n/index.json
    // Custom translations for a module name and a language: https://sdk.onfido.com/capture/i18n/welcome/en_US.min.json
    // Commons translations for a language: https://sdk.onfido.com/capture/i18n/common/en_US.min.json
    private final Map<String, String> customEnglishTranslations = Map.of(
        "welcome.title", "Custom welcome title",
        "welcome.button.default", "Custom button text"
    );
    private final Map<String, Map<String, String>> translationOverrides = Map.ofEntries(
        Map.entry("en_US", customEnglishTranslations)
    );
    private final Localisation customTranslations = new Localisation(
        "en_US",
        List.of("en_US"),
        translationOverrides
    );

    Branding branding = new Branding(
        "Flex app",
        "https://upload.wikimedia.org/wikipedia/commons/d/d7/Android_robot.svg"
    );

    // pass RGBA HEX colors, we internally convert them to ARGB
    Map<ColorTokens, String> colors = Map.of(ColorTokens.BackgroundColorOverlay, "#10598A85");
    Theme theme = new Theme(
        null,
        null,
        branding,
        colors,
        colors,
        null
    );

    private final ClassicParameters classicFlowParameters = new ClassicParameters(
        sdkToken,
        classicSteps,
        new Configuration(false, theme, customTranslations)
    );

    @SuppressWarnings("unused")
    private final StudioParameters studioFlowParameters = new StudioParameters(
        studioToken,
        new Configuration(false, theme, customTranslations)
    );

    private final EntrustIDV sdk = new EntrustIDV(
        this,
        new Callbacks(
            onComplete -> {
                Log.d("JavaActivity", "The Entrust IDV flow was completed successfully with result " + onComplete);
                finish();
                return null;
            },
            error -> {
                Log.e(
                    "JavaActivity",
                    "An error of type " + error.getType() + " occurred in the Entrust IDV flow: " + error.getMessage()
                );
                finish();
                return null;
            },
            userAction -> {
                Log.d("JavaActivity", "The user exited the Entrust IDV flow. Reason: " + userAction);
                finish();
                return null;
            },
            null,
            null,
            null
        )
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        sdk.start(classicFlowParameters); // For studio flows, use: sdk.start(studioFlowParameters) instead
    }
}

