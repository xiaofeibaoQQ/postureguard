"""PostureGuard AI module: forward-head-posture scoring from a webcam.

Frames are processed in memory only. Nothing is saved or uploaded.

Keys: c = calibrate (sit upright, 10 s), q = quit.

Modes
  front: camera faces you. Feature = (shoulder-mid y - nose y) / shoulder width.
         It shrinks as the head drops or leans forward.
  side : camera sees your profile. Feature = |ear x - shoulder x| / |ear y - shoulder y|
         (roughly tan of the ear-shoulder angle from vertical). It grows as the head
         moves ahead of the shoulder.

The score is a z-score against your own calibrated baseline, so it measures change
relative to you, not a clinical angle.
"""
import argparse
import statistics
import time

import cv2
import mediapipe as mp

PoseLandmark = mp.solutions.pose.PoseLandmark
CALIBRATION_SECONDS = 10.0
MIN_SPREAD = 0.02  # avoids huge scores when calibration is very steady


def feature_front(lm):
    ls, rs = lm[PoseLandmark.LEFT_SHOULDER], lm[PoseLandmark.RIGHT_SHOULDER]
    nose = lm[PoseLandmark.NOSE]
    width = abs(ls.x - rs.x)
    if width < 1e-3:
        return None
    mid_y = (ls.y + rs.y) / 2.0
    return (mid_y - nose.y) / width


def feature_side(lm):
    # Use whichever side is more visible to the camera.
    left = lm[PoseLandmark.LEFT_EAR].visibility + lm[PoseLandmark.LEFT_SHOULDER].visibility
    right = lm[PoseLandmark.RIGHT_EAR].visibility + lm[PoseLandmark.RIGHT_SHOULDER].visibility
    ear_id, sh_id = (
        (PoseLandmark.LEFT_EAR, PoseLandmark.LEFT_SHOULDER)
        if left >= right
        else (PoseLandmark.RIGHT_EAR, PoseLandmark.RIGHT_SHOULDER)
    )
    ear, sh = lm[ear_id], lm[sh_id]
    dy = abs(ear.y - sh.y)
    if dy < 1e-3:
        return None
    return abs(ear.x - sh.x) / dy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["front", "side"], default="front")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--warn-z", type=float, default=2.0, help="score that counts as bad posture")
    ap.add_argument("--hold-seconds", type=float, default=3.0, help="how long it must persist")
    args = ap.parse_args()

    feat = feature_front if args.mode == "front" else feature_side
    sign = -1.0 if args.mode == "front" else 1.0  # front: smaller is worse; side: larger is worse

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit("Cannot open camera. Try --camera 1.")

    baseline_mean = baseline_std = None
    calibrating_until = None
    samples = []
    bad_since = None

    with mp.solutions.pose.Pose(model_complexity=0, min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as pose:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            status, color = "No person detected", (160, 160, 160)

            if res.pose_landmarks:
                f = feat(res.pose_landmarks.landmark)
                now = time.time()
                if f is not None:
                    if calibrating_until is not None:
                        samples.append(f)
                        left = calibrating_until - now
                        status, color = f"Calibrating... {max(left, 0):.0f}s (sit upright)", (255, 200, 0)
                        if left <= 0 and len(samples) >= 10:
                            baseline_mean = statistics.fmean(samples)
                            baseline_std = max(statistics.pstdev(samples), MIN_SPREAD)
                            calibrating_until, samples = None, []
                    elif baseline_mean is None:
                        status = "Press 'c' to calibrate"
                    else:
                        z = sign * (f - baseline_mean) / baseline_std
                        bad = z > args.warn_z
                        if bad:
                            bad_since = bad_since or now
                        else:
                            bad_since = None
                        held = bad_since is not None and (now - bad_since) >= args.hold_seconds
                        if held:
                            status, color = f"Neck forward! score {z:.1f}", (40, 40, 230)
                        else:
                            status, color = f"OK  score {z:.1f}", (80, 200, 80)

            cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
            cv2.putText(frame, "c: calibrate   q: quit   (no frames are saved)", (20, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1)
            cv2.imshow("PostureGuard", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                calibrating_until, samples = time.time() + CALIBRATION_SECONDS, []
                baseline_mean = baseline_std = None
                bad_since = None

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
