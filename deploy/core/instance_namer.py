import os
import sys
from utils.logger import log_info, log_warn


class InstanceNamer:
    """Instance naming helper."""

    @staticmethod
    def sanitize(name: str) -> str:
        """Normalize instance name: allow a-z, 0-9, - and _."""
        safe = []
        for c in name.lower():
            if c.isalnum() or c in "-_":
                safe.append(c)
            else:
                safe.append("-")
        return "".join(safe)

    @staticmethod
    def auto_generate(base_path: str) -> str:
        """Generate instance-001 / instance-002 / ..."""

        n = 1
        while True:
            candidate = f"instance-{n:03d}"
            full_path = os.path.join(base_path, candidate)
            if not os.path.exists(full_path):
                return candidate
            n += 1

    @staticmethod
    def handle_conflict(base_path: str, name: str) -> str:
        """If the name exists, append a suffix to avoid conflict."""
        if not os.path.exists(os.path.join(base_path, name)):
            return name

        log_warn(f"Instance name '{name}' already exists, appending a suffix to avoid conflict.")

        n = 2
        while True:
            new_name = f"{name}-{n}"
            full_path = os.path.join(base_path, new_name)
            if not os.path.exists(full_path):
                return new_name
            n += 1

    @staticmethod
    def _read_input(prompt: str) -> str:
        """Read user input; prefer interactive stdin, fallback to terminal device."""

        if sys.stdin and sys.stdin.isatty():
            try:
                return input(prompt)
            except EOFError:
                return ""

        tty_path = "CON" if os.name == "nt" else "/dev/tty"
        try:
            with open(tty_path, "r") as tty:
                print(prompt, end="", flush=True)
                return tty.readline()
        except Exception:
            log_warn("Unable to read user input; will auto-generate instance name.")
            return ""

    @staticmethod
    def ask_name(base_path: str) -> str:
        """
        Ask for instance name:
        - empty -> auto-generate ID
        - custom -> sanitize + conflict check
        """

        print()
        user_input = InstanceNamer._read_input("Please enter instance name (leave empty to auto-generate): ").strip()

        if user_input == "":
            log_info("No user input detected; auto-generating instance name.")
            name = InstanceNamer.auto_generate(base_path)
            log_info(f"Auto-generated instance name: {name}")
            return name

        clean = InstanceNamer.sanitize(user_input)

        if clean == "":
            log_warn("Input contains no valid characters; auto-generating instance ID.")
            return InstanceNamer.auto_generate(base_path)

        final = InstanceNamer.handle_conflict(base_path, clean)

        log_info(f"Instance name confirmed: {final}")
        return final
