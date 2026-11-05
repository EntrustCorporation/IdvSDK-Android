# SDK Size — Android (arm64-v8a)

_Generated on 2026-11-05 · SDK version: 100.18.0_

## Individual Module Impacts

| Package | Base | Size Increase Android (arm64) (Package − Base) |
|---------|------|------------------------------------------------|
| Core | Sample Native App (not using Compose UI) | 1.96 MB |
| Welcome | Core | 0.86 MB |
| Face Photo | Core | 1.21 MB |
| Face Motion | Core | 3.32 MB |
| Document | Core | 3.83 MB |
| Face Motion | Core + Document | 0.37 MB |
| NFC | Core + Document | 1.72 MB |
| Biometric Token | Core | 0.86 MB |
| Retry | Core | 0.85 MB |
| All Native Modules | Core | 5.98 MB |

### How to read this table

- **Package** - the SDK module being measured.
- **Base** - the APK configuration this module was added on top of.
- **Size Increase (Package - Base)** - how much the APK size grew after adding the Package on top of the Base. Modules that share dependencies with the Base will show a smaller increase.

## Commonly Used Combinations

The table above measures each module in isolation, which does not show the cost of a realistic integration. The table below measures the combinations customers actually ship.

| Combination | Size Increase Android (arm64) (Combination − Core) |
|-------------|----------------------------------------------------|
| Core | — (baseline, 1.96 MB total) |
| Core + Document | 3.83 MB |
| Core + Document + Face Photo | 3.87 MB |
| Core + Document + Face Motion | 4.20 MB |
| Core + Document + NFC | 5.55 MB |
| Core + Document + NFC + Face Photo | 5.58 MB |
| Core + Document + NFC + Face Motion | 5.91 MB |

> **Note on shared dependencies**
>
> Each row above is measured from a real APK built with exactly that set of modules, so it is not the sum of the individual rows in the previous table — it is lower.
>
> Document, Face Photo, Face Motion and NFC all depend on the same internal security, networking and UI components. When several of them are included, those shared components are merged and de-duplicated once by the Android build, rather than counted once per module.

### How to read this table

- **Combination** - the full set of SDK modules included in the measured APK.
- **Size Increase (Combination - Core)** - how much larger that APK is than the Core-only APK. Adding the first capture module costs the most, because it brings in the shared components that every later module then reuses.
