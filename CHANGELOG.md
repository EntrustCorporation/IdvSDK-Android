## 100.6.4

### Changed

- Use Studio toggle for enabling Randomness without experimental flag
- Utilize settings panel to enable NFC

### Fixed

- Fix Banner text being clipped when system font is scaled up

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
