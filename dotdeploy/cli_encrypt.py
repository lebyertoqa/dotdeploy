"""CLI sub-commands for snapshot encryption/decryption."""

from pathlib import Path

from dotdeploy.encrypt import EncryptError, decrypt_file, encrypt_file
from dotdeploy.snapshot import _snapshot_dir


def _get_config(args):
    from dotdeploy.config import Config

    return Config(args.config)


def cmd_encrypt_snapshot(args) -> int:
    cfg = _get_config(args)
    snap_dir = _snapshot_dir(cfg)
    src = snap_dir / args.snapshot
    dst = snap_dir / (args.snapshot + ".enc")
    try:
        encrypt_file(src, dst)
        if args.remove_plain:
            src.unlink()
        print(f"Encrypted: {dst}")
        return 0
    except EncryptError as exc:
        print(f"Error: {exc}")
        return 1


def cmd_decrypt_snapshot(args) -> int:
    cfg = _get_config(args)
    snap_dir = _snapshot_dir(cfg)
    src = snap_dir / args.snapshot
    # Allow caller to omit the .enc suffix
    if not src.exists() and not args.snapshot.endswith(".enc"):
        src = snap_dir / (args.snapshot + ".enc")
    out_name = src.stem if src.name.endswith(".enc") else src.name + ".dec"
    dst = snap_dir / (args.output or out_name)
    try:
        decrypt_file(src, dst)
        print(f"Decrypted: {dst}")
        return 0
    except EncryptError as exc:
        print(f"Error: {exc}")
        return 1


def register_encrypt_subcommands(sub) -> None:
    # encrypt
    p_enc = sub.add_parser("encrypt", help="Encrypt a snapshot file")
    p_enc.add_argument("snapshot", help="Snapshot filename inside snapshot dir")
    p_enc.add_argument(
        "--remove-plain",
        action="store_true",
        default=False,
        help="Delete plaintext snapshot after encryption",
    )
    p_enc.set_defaults(func=cmd_encrypt_snapshot)

    # decrypt
    p_dec = sub.add_parser("decrypt", help="Decrypt an encrypted snapshot file")
    p_dec.add_argument("snapshot", help="Encrypted snapshot filename (.enc)")
    p_dec.add_argument(
        "--output",
        default=None,
        help="Output filename (default: strip .enc suffix)",
    )
    p_dec.set_defaults(func=cmd_decrypt_snapshot)
