## 100.13.0

### Fixed

- Fixes the country selector in Document capture being announced as a drop-down list by TalkBack. It now announces as a button, matching the separate screen it opens
- Fixed TalkBack not announcing the title as a heading on status screens (such as the unsupported/unaccepted document page). The title now receives accessibility focus and is announced as a heading when the screen appears, consistent with content screens.

## 100.12.0

### Changed

- XML translation overrides declared in the integrating app are now applied even when the SDK is delivered as a dynamic feature module.
- Connectivity failures (DNS, socket, TLS, and retry-exhaustion errors) are now reported to the crash reporting pipeline at log level WARNING instead of ERROR, since they are expected/environmental rather than SDK defects. These failures are also now classified as ErrorType.NetworkException in the onError callback instead of falling through to ErrorType.GenericException, so integrators handling errors by type can distinguish connectivity issues and build dedicated "check your connection" / retry UX. Unrelated failures (e.g. malformed server responses) are unaffected and continue to report ErrorType.GenericException at ERROR
- The document selection screen is now skipped automatically when only a single document type and country are configured

### Fixed

- A backend authentication failure (401/403) is now reported to the crash reporting pipeline once instead of two or three times. BackendErrorInterceptor previously threw an SdkException, which OkHttp cannot deliver from an interceptor, so the same failure was reported again as a wrapped "canceled due to ..." IOException and once more through the default uncaught exception handler. The ErrorType surfaced to integrators through onError is unchanged
- Terminal conditions the SDK cannot prevent - an expired or invalid token, an exhausted trial, a geo-blocked request, connectivity failures, and media upload failures - are now reported to the crash reporting pipeline at log level WARNING instead of ERROR. Severity is derived from ErrorType.category in the shared error contract, so a new error type inherits the right severity without an SDK change. Failures that may be SDK defects continue to report at ERROR
- A failed analytics request no longer ends the flow. Analytics shares the authenticated HTTP client, so a 401 or 403 on a telemetry request previously terminated the verification flow through onError. That failure is now ignored and the flow continues; a genuine authentication failure still surfaces on the next API call
- Fixed a hard, non-retryable verification failure ("Unable to load PublicSuffixDatabase.list resource.") in apps that resolve an Android build of OkHttp 5.x. The SDK runs its verification flow in a separate process, and OkHttp 5.x reads its public suffix list through an Android context that is only set in the default process. The SDK now sets that context in the process it owns, so you no longer need to call okhttp3.OkHttp.initialize(applicationContext) from Application.onCreate() as a workaround.
- DNS resolution now falls back to the system resolver on any resolver failure rather than only UnknownHostException, so a resolver that breaks the OkHttp contract degrades instead of aborting the call.

## 100.11.0

### Added

- Adds on-device image quality assessment for Motion capture, checking frame sharpness, brightness, and contrast before/during recording

### Changed

- Update scan button colors on the document capture screen

### Fixed

- Fixes several progress/spinner indicators not reflecting the integrator's configured brand color: the splash screen spinner (RGBA hex colors were parsed as ARGB), the external link/PDF preview bottom sheet spinner (previously not themed at all, and stuck showing a static grey track instead of animating), and the NFC chip-scanning bottom sheet's progress ring (was hardcoded to a legacy blue instead of the brand color)
- Fixed a startup slowdown on networks that block public DNS-over-HTTPS resolvers, where the SDK could sit on the loading screen for far longer than expected before the first screen appeared. API hosts are now resolved with the device DNS resolver first and DNS-over-HTTPS is used only when the device resolver fails, so a blocked resolver no longer delays startup. Successful lookups are also cached for the session, and a repeatedly failing DNS-over-HTTPS endpoint is skipped for the remainder of the session.
- Fixed a startup slowdown where the SDK could stay on the loading screen for an extended time before the first screen appeared on networks where the Cloudflare DNS-over-HTTPS resolver is blocked or slow. DoH lookups are now tightly time-bounded and fall back to the system DNS quickly, the SDK client no longer waits indefinitely to establish a connection, and independent startup requests are performed concurrently.

## 100.10.0

### Added

- Adds on-device image quality assessment for Motion capture, checking frame sharpness, brightness, and contrast before/during recording

### Changed

- Update scan button colors on the document capture screen

### Fixed

- Fixes several progress/spinner indicators not reflecting the integrator's configured brand color: the splash screen spinner (RGBA hex colors were parsed as ARGB), the external link/PDF preview bottom sheet spinner (previously not themed at all, and stuck showing a static grey track instead of animating), and the NFC chip-scanning bottom sheet's progress ring (was hardcoded to a legacy blue instead of the brand color)
- Fixed a startup slowdown where the SDK could stay on the loading screen for an extended time before the first screen appeared on networks where the Cloudflare DNS-over-HTTPS resolver is blocked or slow. DoH lookups are now tightly time-bounded and fall back to the system DNS quickly, the SDK client no longer waits indefinitely to establish a connection, and independent startup requests are performed concurrently.

## 100.9.0

### Fixed

- Fixed TalkBack not announcing the title as a heading on status screens (such as the unsupported/unaccepted document page). The title now receives accessibility focus and is announced as a heading when the screen appears, consistent with content screens.

## 100.8.0

### Added

- Support custom remote fonts: integrators can now pass a `ResourceLocation.Remote` URL in their `SdkFont` list and it is downloaded, cached, and applied across all native modules before any screen renders. The font download is best-effort with a 20 MB size cap and a 15 s timeout; if loading fails the SDK falls back to the system font and logs an error. OTF fonts require API 26+; on older devices OTF sources are skipped and the next TTF source or system font is used instead. Web modules already support remote fonts and are unaffected. Additionally, custom font sources are now applied in the order declared by the integrator (previously TTF was silently preferred over OTF).

### Changed

- Utilize settings panel to enable NFC
- Improved the accessibility of the document and country selection bottom sheets. The close (drag handle) control is now exposed to screen readers with an appropriate button role and accessible name, instead of relying on the interaction hint alone.
- Improved the accessibility of document capture warning icons. The informative icons shown in the live capture feedback and the capture warning bottom sheet now provide a text alternative to screen readers, so their meaning is no longer conveyed by the icon alone.
- Improved the accessibility of the document upload success screen. The informative success icon shown above the "ID submitted" confirmation now provides a text alternative to screen readers, so its meaning is no longer conveyed by the icon alone.
- Increased contrast of the inactive page indicator dot colour on document help carousel

### Fixed

- Fixed an issue where Motion video uploads could occasionally fail due to exceeding the upload size limit.
- Fixed an issue where autocapture was not functioning on slow network connections. ML models required for autocapture now fall back to manual capture if they fail to initialise within the configured timeout.
- Fix Banner text being clipped when system font is scaled up
- Fix network requests being cancelled during retries by closing the previous response before retrying, preventing an IllegalStateException ("cannot make a new request because the previous response is still open").
- Improved accessibility of advisory banners: screen readers now announce the banner's type (e.g. "Information:") before its text, and the decorative banner icon is no longer a separate focus stop.
- Improved accessibility of error status screens: screen readers now announce "Error:" before the heading so the meaning of the error icon is conveyed, and the icon itself is not part of the screen reader traversal.
- Fixed the "Error:" prefix not being announced by TalkBack on error status screens (such as the Motion "We can't detect your face" screen) when the heading received screen reader focus on load.
- Improved accessibility of the motion capture success state: screen readers now announce "Success:" before the completion message, and the success icon is hidden from screen reader traversal.

## 100.7.0

### Added

- On Studio flows now honor the welcome screen configuration returned by the SDK Configuration API. When the welcome screen is disabled on Studio for a workflow, it is no longer shown at the start of the flow; otherwise the existing behavior is kept.

### Fixed

- Fixed the biometric token handler (`onTokenGenerated`) never firing on release builds.
- Do not attempt NFC flow when NFC module is not integrated
- Fix intro animations disappearing after dismissing the alert dialog
- Fixed WorkManager crash caused by large payloads exceeding the 10 KB Data limit.
- Improve SDK launch reliability and startup UX by adding a splash handoff flow, startup loader, and theme-aware startup system bars.

## 100.6.3

### Changed

- Use Studio toggle for enabling Randomness without experimental flag

## 100.6.2

### Fixed

- Fixed a silent crash in Motion when the VIBRATE permission declaration is removed from the merged Manifest file
- Prevent 3rd-party apps from reacting to NFC while the SDK is in the foreground
- Fix Document capture intro screen animation being announced twice by TalkBack.
- Fixed screen reader traversal order in Document Capture Intro and Motion Intro screens.
- Fixed screen reader focus of the Play/Pause button in Motion Intro screen 

## 100.6.1

### Changed

- Changed the translations overrides validation: we now allow passing **empty** strings as valid values for a translation key. This effectively means that when a custom empty translation is passed to the SDK for a certain translation key, it will not be displayed in the UI.

### Fixed

- Fixed an issue with the Face Motion capture upload in the context of Studio task timeouts. This is now calling `onError` in this scenario, to ensure consistency with the other capture experiences like Document

## 100.6.0

### Added

- Added the ability to detect and handle multiple faces during the Motion capture flow
- Added previous/next buttons in the Document capture bottom sheet help dialog

### Changed

- Added Button role to document types card items and BottomSheetHandle for better Talkback experience.

### Fixed

- Fix status bar colour and navigation bar shift regression on capture screens and country picker
- Fixed TalkBack not announcing animations on the NFC instruction screen, Face Motion instruction screen, and Document instruction screen.
- Fixed TalkBack accessibility on the document intro screen: the animation is now focusable with a descriptive label, and the Play/Pause buttons announce their role and name correctly.

## 100.5.0

### Changed

- Update the NFC animations to use a 16:9 format
- Add support for custom font files placed in res/font/ via the `res://font/<name>` URI scheme in `ResourceLocation.Local`, alongside the existing file:///android_asset/ scheme
- Downgraded compose to version 2025.02.00 to stay as minmimum as possible to avoid version conflicts with clients.

## 100.4.0

### Added

- Implemented Live Selfie Authentication and Light Onboarding-Verify Liveness SDK features
- Added support for custom local fonts. Integrators can now provide a custom local (bundled) font via `Theme.resources.fonts`, applied across both native and web modules
- Allow customization for selection list item border radius
- Added a script to the integration-sample app for enterprise customers to download SDK artifacts seamlessly

### Changed

- Applied round shape to Play/Pause button
- Expose `buttonBorderRadius` and `selectionListItemBorderRadius` as public `Theme` dimension tokens via `BorderRadiusTokens`. This allows the customization of the button border radius and selectable list items' border radius (used in the document selection and country selection screens)

### Fixed

- Fixed an issue with the Biometric token retrieval
- Fixed a serialization runtime issue in `-k19` versions when using Kotlin 1.9.x (Kotlin 2.0.x integrators/builds were unaffected)

## 100.2.1

### Fixed

- Fixed the issue where `ProofOfAddress` flows get stuck in an infinite loading screen after submission

## 100.2.0

### Added

- Introduced a `-k19` variant of our modules compatible with the Kotlin 1.9 compiler

## 100.1.0

### Added

- Added `SplitCompat.install` to the SDK activity to fix a crash when launching the SDK in a DFM
- Added support for launching the SDK using `android.app.Activity` (Onfido Android SDK)

## 100.0.0

### Fixed

- Fixed incorrect loading of bundled translations resources
- Fixed callbacks crash

## 0.1.3-beta1

### Added

- Support e-signature capture on Android
- Added a public API configuration option for the top navigation bar inside the SDK screens
- Publish sample app to Github
- Upgrade and update integrator sample app

### Changed

- Renamed the Onfido process (`onfido_process`) to Entrust (`entrust_idv_process`), as well as the `isOnfidoProcess` utility extension to `isEntrustIDVProcess`

## 0.0.2-beta1

### Added

- Introduction of the logo and text co-branding initialization options. This feature no longer requires prior activation

### Changed

- Finished the `onComplete` callback
- Added `onComplete` result serialization and mapping from the individual module output to `CaptureResult`
- Finished the `onError` callback

### Fixed

- Fixed translations not working for regional localization (cases such as `pt_BR`, `pt_PT`)
- Fixed the icon rendering in a List with icons: the size and alignment to the top. This type of list can be shown in any Intro screen
