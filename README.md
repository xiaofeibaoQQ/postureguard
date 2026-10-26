# PostureGuard

A lightweight wearable and AI companion that keeps your eyes at a safe distance and your neck in line.

> Hackathon 2026 · Team 好累對不隊 · 吳宥勳
> Status: hackathon prototype. PostureGuard is a wellness aid, not a medical device.

## Why

Heavy phone and laptop use encourages two silent habits: holding screens too close and letting the head drift forward. Both are linked to digital eye strain, myopia risk and neck pain, yet people rarely notice the moment it happens.

## What it does

| Module | What it senses | How |
|---|---|---|
| **A. Wearable distance sensor** | Eye-to-screen distance and head pitch | Time-of-flight (ToF) sensor and IMU on glasses or headphones, streamed over BLE |
| **B. Neck-posture vision** | Forward head posture | Opt-in camera, MediaPipe Pose, on-device scoring. No frame is stored or uploaded |

A companion app fuses both signals with screen context and nudges the user (haptic pulse, on-screen toast) using debounce, hysteresis, cooldown and context gating.

## Repository layout

```
ai/         Pose pipeline and calibration (runnable demo included)
app/        Companion app (Flutter / Python desktop client)
firmware/   Wearable firmware (nRF52840, Zephyr)
hardware/   Bill of materials, wiring, enclosure files
docs/       Architecture, BLE GATT spec, images
```

## Quick start: AI module (works today, laptop webcam only)

```bash
cd ai
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python posture_demo.py --mode front      # or: --mode side
```

1. Sit upright and press `c` to calibrate for 10 seconds.
2. Lean your head forward: the score rises and a warning appears.
3. Press `q` to quit.

Frames stay in memory only; nothing is saved or sent anywhere.

## Architecture

See [docs/architecture.md](docs/architecture.md) and [docs/ble-gatt.md](docs/ble-gatt.md).

## Roadmap

- [x] Pose scoring demo with calibration
- [ ] Firmware: ToF + IMU sampling, BLE GATT server, haptics
- [ ] App: BLE client, fusion and alert engine, dashboard
- [ ] Enclosure and power test
- [ ] Pilot with volunteers

Update the checkboxes honestly as parts get built.

## Privacy

Camera features are opt-in, processed on-device, and never store or upload frames. Cloud sync is off by default.

## References

1. Hansraj, K. K. (2014). Assessment of stresses in the cervical spine caused by posture and position of the head. *Surgical Technology International*, 25.
2. Huang, H.-M., Chang, D. S.-T., & Wu, P.-C. (2015). Near work activities and myopia in children: a systematic review and meta-analysis. *PLOS ONE*, 10(10).
3. Sheppard, A. L., & Wolffsohn, J. S. (2018). Digital eye strain: prevalence, measurement and amelioration. *BMJ Open Ophthalmology*, 3(1).
4. Bazarevsky, V., et al. (2020). BlazePose: On-device real-time body pose tracking. arXiv:2006.10204.

## License

MIT, see [LICENSE](LICENSE).
