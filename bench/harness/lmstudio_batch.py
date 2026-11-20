#!/usr/bin/env python3
"""Run the handoff suite on several LM Studio models, one after another.

    python bench/harness/lmstudio_batch.py --models qwen3.5-9b,gemma-4-e4b-it --n 60

For each model: wait until it is downloaded, unload everything, load it, run
bench/harness/run.py, then write its summary with report.py. Models that fit
in GPU memory are loaded fully onto the GPU; larger ones use LM Studio's
automatic CPU/GPU split. Extra arguments after `--` go to run.py unchanged.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_LMS = os.path.join(os.path.expanduser("~"), ".lmstudio", "bin", "lms.exe" if os.name == "nt" else "lms")


def lms(args, binary, check=True):
    out = subprocess.run([binary] + args, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", stdin=subprocess.DEVNULL)
    if check and out.returncode != 0:
        raise RuntimeError(f"lms {' '.join(args)} failed: {out.stderr.strip()[-300:]}")
    return out.stdout


def downloaded(binary):
    return {m["modelKey"]: m for m in json.loads(lms(["ls", "--llm", "--json"], binary) or "[]")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    passthrough = []
    if "--" in argv:
        i = argv.index("--")
        argv, passthrough = argv[:i], argv[i + 1:]
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--models", required=True, help="comma-separated LM Studio model keys")
    p.add_argument("--n", type=int, default=60)
    p.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    p.add_argument("--lms", default=DEFAULT_LMS)
    p.add_argument("--context", type=int, default=16384)
    p.add_argument("--gpu-gb", type=float, default=7.0,
                   help="load fully on GPU when the model file is smaller than this")
    p.add_argument("--wait-minutes", type=int, default=600, help="how long to wait for a download")
    args = p.parse_args(argv)

    for model in [m.strip() for m in args.models.split(",") if m.strip()]:
        deadline = time.time() + args.wait_minutes * 60
        while model not in downloaded(args.lms):
            if time.time() > deadline:
                print(f"{model}: not downloaded after {args.wait_minutes} min, skipping", flush=True)
                break
            time.sleep(60)
        info = downloaded(args.lms).get(model)
        if not info:
            continue
        lms(["unload", "--all"], args.lms, check=False)
        load = ["load", model, "--context-length", str(args.context), "-y"]
        if info["sizeBytes"] < args.gpu_gb * 1e9:
            load += ["--gpu", "max"]
        print(f"=== {model}: loading ({info['sizeBytes'] / 1e9:.1f} GB)", flush=True)
        try:
            lms(load, args.lms)
        except RuntimeError as e:
            print(f"{model}: {e}", flush=True)
            continue
        started = time.time()
        subprocess.run([sys.executable, os.path.join(HERE, "run.py"), "--model", model, "--n", str(args.n),
                        "--base-url", args.base_url] + passthrough, stdin=subprocess.DEVNULL)
        print(f"=== {model}: finished in {(time.time() - started) / 60:.0f} min", flush=True)
        subprocess.run([sys.executable, os.path.join(HERE, "report.py"),
                        os.path.join(ROOT, "bench", "results", "handoff", model), "--write"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    lms(["unload", "--all"], args.lms, check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
