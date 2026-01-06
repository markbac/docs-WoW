
# Firmware Development Breakdown and RAID Log

## 📋 Feature and User Story Estimates (With Feature Totals)

| **Feature**                                | **User Story / Task**                                         | **Estimate (Days)** | **Feature Total** |
| ------------------------------------------ | ------------------------------------------------------------- | ------------------- | ----------------- |
| **G191 UMU**                               | Wakeup from UMM                                               | 5                   | **24**            |
|                                            | Support new alarms                                            | 5                   |                   |
|                                            | “A” button                                                    | 5                   |                   |
|                                            | PAYG registers                                                | 3                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Unit tests                                                    | 3                   |                   |
| **Valve Control – Credit Mode (Post Pay)** | Understand doc 6480 behaviour                                 | 3                   | **19**            |
|                                            | Investigate ARM state addition + add if needed                | 10                  |                   |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Unit tests                                                    | 3                   |                   |
| **PAYG Credit, Value, Emergency & Valve**  | Design document SM                                            | 10                  | **51**            |
|                                            | Handle using credit                                           | 5                   |                   |
|                                            | Credit adjust                                                 | 5                   |                   |
|                                            | Top-up                                                        | 5                   |                   |
|                                            | CoT integration                                               | 3                   |                   |
|                                            | Emergency selected                                            | 5                   |                   |
|                                            | LwM2M integration                                             | 5                   |                   |
|                                            | UI menu                                                       | 5                   |                   |
|                                            | Low credit threshold warning                                  | 3                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Unit tests                                                    | 2                   |                   |
| **CoT**                                    | Process LwM2M command                                         | 3                   | **22**            |
|                                            | Future dated command                                          | 3                   |                   |
|                                            | Report PAYG status + clear                                    | 3                   |                   |
|                                            | Clear profile data                                            | 5                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Unit tests                                                    | 5                   |                   |
| **Certificates / Security**                | DTLS overview (ciphers, cycles)                               | 5                   | **59**            |
|                                            | Understand DTLS doc (incl. production injection, error tests) | 10                  |                   |
|                                            | DTLS for FOTA                                                 | 10                  |                   |
|                                            | Understand Root CA + cert chain                               | 5                   |                   |
|                                            | Add certs for OTP (per G470)                                  | 3                   |                   |
|                                            | Production process (OTP)                                      | 5                   |                   |
|                                            | Add certs for secure boot (per G476)                          | 3                   |                   |
|                                            | Production process (secure boot)                              | 5                   |                   |
|                                            | Documentation                                                 | 10                  |                   |
|                                            | Unit tests                                                    | 3                   |                   |
| **Secure Boot**                            | Investigate SiLabs secure boot                                | 5                   | **32**            |
|                                            | Investigate current bootloader                                | 3                   |                   |
|                                            | Implement secure boot                                         | 10                  |                   |
|                                            | Support FOTA                                                  | 10                  |                   |
|                                            | Unit tests                                                    | 1                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
| **Attestation**                            | Create new LwM2M object                                       | 3                   | **32**            |
|                                            | Implement CMAC                                                | 5                   |                   |
|                                            | Calculate CMAC of flash                                       | 20                  |                   |
|                                            | Create LwM2M link                                             | 1                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
| **OTP**                                    | Read SMETS + understand GMAC + replay                         | 5                   | **57**            |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Understand G470 UTRN code                                     | 5                   |                   |
|                                            | Documentation (further detail)                                | 3                   |                   |
|                                            | GMAC validation                                               | 10                  |                   |
|                                            | Veerhoff validation                                           | 3                   |                   |
|                                            | Extract volume + apply to SM                                  | 5                   |                   |
|                                            | Handle events (reboot, SWOS, error, cryptofail)               | 3                   |                   |
|                                            | Replay protection incl. cache                                 | 7                   |                   |
|                                            | Documentation                                                 | 3                   |                   |
|                                            | Unit tests                                                    | 10                  |                   |
| **LwM2M**                                  | Doc – how to create objects                                   | 3                   | **52**            |
|                                            | Create crypto & new object                                    | 3                   |                   |
|                                            | Define objects                                                | 3                   |                   |
|                                            | Unit tests                                                    | 3                   |                   |
|                                            | Friendly integration – standard objects                       | 10                  |                   |
|                                            | Friendly integration – custom objects                         | 10                  |                   |
|                                            | Friendly integration – bootstrap                              | 20                  |                   |
| **Board Bring-Up**                         | Serial flash                                                  | 3                   | **32**            |
|                                            | GPIO changes (peripherals)                                    | 3                   |                   |
|                                            | UART clocks                                                   | 5                   |                   |
|                                            | Modem + power control                                         | 7                   |                   |
|                                            | Galvanic                                                      | 1                   |                   |
|                                            | G191                                                          | 5                   |                   |
|                                            | Tamper                                                        | 1                   |                   |
|                                            | Buttons                                                       | 1                   |                   |
|                                            | Display (GPIO/backlight)                                      | 5                   |                   |
|                                            | Energy suite run                                              | 1                   |                   |
| **Local Firmware Update**                  | Document it                                                   | 3                   | **9**             |
|                                            | Test create OTA + doc                                         | 3                   |                   |
|                                            | Test                                                          | 3                   |                   |
| **Battery Door Tamper**                    | App MCU interrupt                                             | 1                   | **10**            |
|                                            | Event (as any tamper)                                         | 1                   |                   |
|                                            | Test                                                          | 3                   |                   |
|                                            | New hardware validation                                       | 3                   |                   |
|                                            | Unit test                                                     | 1                   |                   |
|                                            | Documentation                                                 | 1                   |                   |
| **Magnetic Tamper**                        | Initial integration                                           | 1                   | **16**            |
|                                            | Event handling                                                | 5                   |                   |
|                                            | Tools                                                         | 3                   |                   |
|                                            | New hardware                                                  | 3                   |                   |
|                                            | Unit test                                                     | 3                   |                   |
|                                            | Documentation                                                 | 1                   |                   |
| **Production Test Firmware (Post-New HW)** | Understand current FW + documentation                         | 5                   | **15**            |
|                                            | Get running on G460                                           | 3                   |                   |
|                                            | Add new function for HW changes                               | 7                   |                   |
| **Battery Life Counter**                   | Change counter                                                | 1                   | **2**             |
|                                            | Test                                                          | 1                   |                   |
| **Dev – Test Lanes + CI/CD**               | Setup NUC                                                     | 2                   | **14**            |
|                                            | Toolchain setup                                               | 1                   |                   |
|                                            | Setup key T\&V test + pipeline                                | 5                   |                   |
|                                            | Failure analysis                                              | 5                   |                   |
|                                            | Auto-commit map file changes                                  | 1                   |                   |
| **G480 Changes – US**                      | Check features required                                       | —                   | **—**             |
|                                            | Cherry-pick from upstream                                     | —                   |                   |
|                                            | Build                                                         | —                   |                   |
|                                            | Test (no unit)                                                | —                   |                   |
|                                            | PR                                                            | —                   |                   |
| **Review & Signoff**                       | 1-day US for all features                                     | 1                   | **1**             |

**Total (Estimated)**: ≈ 438 days

***

## ⚠️ RAID Log 
| **Type**       | **Item**                                 | **Description / Notes**                                                  |
| -------------- | ---------------------------------------- | ------------------------------------------------------------------------ |
| **Risk**       | Timeliness of HW + G191                  | Hardware availability could delay firmware bring-up.                     |
| **Risk**       | Impact of GDC resource on board bring-up | Competing workload may limit resource availability.                      |
| **Risk**       | Security / Pen testing (microchip)       | Requires coordination and test slot availability.                        |
| **Risk**       | Battery life                             | Calibration and validation accuracy may impact measurement results.      |
| **Risk**       | Friendly ownership & management config   | Misalignment in Friendly/Production configuration may delay integration. |
| **Issue**      | STAG vulnerability                       | Known security exposure under investigation.                             |
| **Issue**      | Friendly integration issues              | Object and API mismatches causing test failures.                         |
| **Assumption** | Hardware 90% OK                          | Minor modifications expected after prototype validation.                 |
| **Assumption** | Early T\&V                               | Test and verification available early in development cycle.              |
| **Assumption** | Friendly support available               | Continuous collaboration from Friendly platform team.                    |
| **Assumption** | G480 baseline sufficient                 | Upstream branch assumed functionally complete for reuse.                 |
| **Assumption** | New Root CA in place (Post-Day-1)        | Security provisioning ready for production.                              |
| **Dependency** | L+G Metrology team                       | Provides metrology validation and test support.                          |
| **Dependency** | L+G Gas FW team                          | Responsible for integration and defect resolution.                       |



