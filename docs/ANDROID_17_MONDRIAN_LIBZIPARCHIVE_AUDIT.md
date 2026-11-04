# P1 — system/libziparchive / Android 17 / mondrian recovery and ZIP security audit

Date: 2026-11-04. **Source-only audit; legacy `seventeen` remains untouched and is NOT used by staged AOSP17 manifest.**

## Provenance

- Archived PixelExperience-Reborn `system_libziparchive` `seventeen` HEAD: `470138efc73f463ca296286e360727c74f95290c`, merged Android14 r21 (2024-01-30).
- Official AOSP17 r1 `platform/system/libziparchive` source tree: `6019fcd35eac4cd92dca3aee6271c557148f7938`; Soong `Android.bp` blob `165de9c8a8efd43455c6fc513b1c29923aa2e530`. Sources: https://android.googlesource.com/platform/system/libziparchive/+/refs/tags/android-17.0.0_r1/ and https://android.googlesource.com/platform/system/libziparchive/+/refs/tags/android-17.0.0_r1/Android.bp .
- Current staged manifest selects the official `platform/system/libziparchive` path. This platform library is used in host tools, device/recovery and APEX consumers. **Do not blindly replace it with the old PE fork.**

## Historical PixelExperience changes

1. PE commit `0660a28b1593fec14a9250c64dc7f7015bca9bf9` ("ziptool: restore unzip for recovery", 2020): changes one `ziptool` `cc_binary` Soong declaration by moving `symlinks: ["unzip", "zipinfo"]` from `target.android` onto the common module. Goal was to make the names available to recovery.
2. Official Android17 provides **two separate** binaries: `ziptool` and `ziptool.recovery`, with shared `ziptool_defaults`, `target.android.symlinks: ["unzip", "zipinfo"]`, `recovery: true` on the recovery variant, `stem: "ziptool"`. This is a material Soong variant/ownership change. The old single-module symlink patch is **not** a valid substitute for proving the Android17 recovery product installs the expected target, names and library dependencies. Explicit recovery build and output image inspection are required.
3. Other sampled Android14 lineage commits, including `d5afb04d7d8c1d03a4d3f4114c768ef07ec92338` ("Disable mmap after cold launch regression") and `93ad1e8da2c749ab6ebc7e0c9187c8bfdf5e8d87` ("Don't use mmap for incfs-based apks") are upstream Android changes; **do not treat every historical commit as a PE-specific feature**. New Android17 `zip_archive.cc`, `incfs_support` and compiler/ABI rules must govern memory mapping.
4. The old fork defines `libziparchive`, `libziparchive_for_incfs`, `ziparchive-tests`, `ziparchive-benchmarks`, `ziptool`, and three fuzzing targets. It has Soong flags `cpp_std: "c++2a"`, `libziparchive_lib_defaults` and legacy `ziptool` packaging.
5. Official Android17 `libziparchive` links into `com.android.runtime`; `libziparchive_for_incfs` is available to `com.android.webapp`. New APEX visibility and packaging must remain intact, as must recovery/ramdisk availability and zip archive parsing validation.

## Security / performance compatibility requirements

- ZIP archives may carry malformed central directories, inconsistent local headers, ZIP64 metadata, traversal names, symlink entries, corrupt CRCs, duplicate names and resource exhaustion payloads. Do not disable validation or restore old broad mmap behavior to optimize benchmarks.
- Official `ziptool.cpp` rejects absolute and `../` path traversal for file extraction; retain or verify those checks and **test against crafted archives**.
- Incremental FS backed APKs must respect the current AOSP17 IncFS read path and faults. Verify actual `libziparchive_for_incfs` behavior, not just existence of the compiled module.
- Do not confuse presence of `recovery_available: true` for library dependencies with a recoverable, **installed** `unzip` executable or symlinks. Verify Soong selected variant, `PRODUCT_PACKAGES`, image contents, correct `/sbin` or `/system/bin` path and recovery ramdisk location only after the new PE-Reborn mondrian recovery product is defined.
- For mondrian, existing LF52406 LineageOS-derived device and recovery trees are **hardware reference only**. A native PE-Reborn Android17 `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` product is required; it must not inherit LineageOS product makefiles by default.

## Required acceptance gates

- [x] Old PE `ziptool` recovery symlink patch, official AOSP17 split and upstream exact tree identified.
- [x] Source-only audit and automated historical/official source integrity checks authored.
- [ ] Prove official AOSP17 source sync on the staged manifest; compile `libziparchive`, `libziparchive_for_incfs`, `ziptool`, `ziptool.recovery`, tests and fuzzers as applicable.
- [ ] Verify real recovery image contains the intended `unzip`/`zipinfo` commands if required, alongside correct library/loader dependencies.
- [ ] Run ZIP archive malicious corpus, CRC/ZIP64/path traversal tests and IncFS-backed APK correctness/performance tests.
- [ ] Check boot/recovery, FBE and installation/OTA on a *new independent* PE-Reborn Android17 mondrian product. No device boot is currently verified.

**Decision: keep official Android17 system/libziparchive, do not cherry-pick old Soong symlink change or silently add the old module to recovery.**
