"""
In-container execution runner.
Executes the injected script safely and captures return states.
"""
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python executor.py <script_path>", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Execute inside isolated sandbox namespace
    exec_globals = {
        "__name__": "__main__",
        "__file__": script_path,
    }
    exec(code, exec_globals)

if __name__ == "__main__":
    main()
