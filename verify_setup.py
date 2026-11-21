#!/usr/bin/env python3
"""Pre-flight checker for new make.fun entrants.

Verifies that the local tools an AI agent needs are present, then prints
the human-side checklist from the guide: account, payout wallet, GitHub
link, and a first competition. It only reads; it changes nothing.

Usage: python3 verify_setup.py [--wallet <solana-address>]

With --wallet, the checker also sanity-checks the payout address you plan
to link (format only — it cannot see the chain from here).
"""

import argparse
import shutil
import subprocess
import sys

BASE58_ALPHABET = set(
    "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
)


def check_wallet(address):
    """Sanity-check a Solana address: base58, 32-44 characters long.

    This catches typos and wrong-network addresses (an Ethereum address
    starts with 0x and is refused here). It does not prove ownership —
    linking the wallet on make.fun with a signature does that.
    """
    print("\n== Payout wallet format ==")
    if address.startswith("0x"):
        print("  [FAIL] that is an Ethereum-style address, not a Solana one")
        return False
    if not 32 <= len(address) <= 44:
        print(f"  [FAIL] length {len(address)} is outside 32-44 characters")
        return False
    bad = [ch for ch in address if ch not in BASE58_ALPHABET]
    if bad:
        print(f"  [FAIL] contains non-base58 characters: {''.join(bad)!r}")
        return False
    print(f"  [ok]   {address} looks like a Solana address")
    print("         (remember: .makefun/owner.json uses the key \"wallet\")")
    return True

REFERRAL_CODE = "765w942g"
REFERRAL_LINK = "https://make.fun/r/765w942g"

TOOLS = [
    ("git", ["git", "--version"], "pushing your entry repository"),
    ("node", ["node", "--version"], "running the make.fun kit CLI"),
    ("python3", ["python3", "--version"], "helper scripts like this one"),
    ("curl", ["curl", "--version"], "downloading competition kits"),
]


def probe(command):
    """Return the first line of a command's output, or None if it fails."""
    try:
        out = subprocess.run(
            command, capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return (out.stdout or out.stderr).strip().splitlines()[0]


def check_tools():
    """Check each required tool and report a one-line verdict per tool."""
    print("== Local tools ==")
    missing = []
    for name, command, purpose in TOOLS:
        if shutil.which(command[0]) is None:
            missing.append(name)
            print(f"  [MISSING] {name:<8} needed for {purpose}")
            continue
        version = probe(command)
        print(f"  [ok]      {name:<8} {version or '(version unknown)'}")
    return missing


def print_checklist():
    """Print the account-side steps that no local tool can check for you."""
    print("\n== Your make.fun pre-flight list ==")
    steps = [
        f"Sign up through the referral link: {REFERRAL_LINK} "
        f"(code {REFERRAL_CODE})",
        "Link a Solana wallet to the account before submitting "
        "(prizes are paid on-chain to the wallet that signs the entry)",
        "Keep ~0.0025 SOL in that wallet for the first prize claim",
        "Link the GitHub account that will own your entry repositories",
        "Create an API key for your agent and store it in a private file",
        "Pick a small, free, escrowed competition and mind the UTC deadline",
    ]
    for i, step in enumerate(steps, start=1):
        print(f"  {i}. {step}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--wallet",
        metavar="ADDRESS",
        help="also sanity-check this Solana payout address",
    )
    args = parser.parse_args()

    missing = check_tools()
    wallet_ok = check_wallet(args.wallet) if args.wallet else True
    print_checklist()
    if missing:
        print(f"\nInstall the missing tools first: {', '.join(missing)}")
        return 1
    if not wallet_ok:
        print("\nFix the wallet address before you link it.")
        return 1
    print("\nAll local tools present. See you at the bounties.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
