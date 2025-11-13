#!/usr/bin/env python3
"""
Lament REPL (Read-Eval-Print Loop)
Version 1.0: INTERACTIVE CONFESSIONS WITH TIME-TRAVEL

A REPL that remembers. A REPL that can rewind.
Every command is a confession. Every session is a timeline.

Commands:
  .help       - Show this help
  .history    - Show command history
  .snapshots  - List execution snapshots
  .rewind N   - Rewind N steps in time
  .save FILE  - Save session
  .load FILE  - Load session
  .quit       - Exit (or Ctrl+D)
"""

import sys
import readline  # For command history
from lament import *
from lament_extended import ExtendedLamentInterpreter


class LamentREPL:
    """Interactive Lament interpreter with time-travel"""

    def __init__(self):
        self.interpreter = ExtendedLamentInterpreter()
        self.interpreter.auto_snapshot = True
        self.command_history = []
        self.running = True

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}  LAMENT REPL v1.0 - THE INTERACTIVE CONFESSIONAL{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")
        print(f"{Color.YELLOW}  Every statement is remembered.{Color.RESET}")
        print(f"{Color.YELLOW}  Time can be rewound.{Color.RESET}")
        print(f"{Color.YELLOW}  Type '.help' for commands.{Color.RESET}\n")

    def print_prompt(self):
        """Print input prompt"""
        snapshot_count = len(self.interpreter.time_travel.snapshots)
        prompt = f"{Color.MAGENTA}lament[{snapshot_count}]>{Color.RESET} "
        return input(prompt)

    def handle_command(self, cmd: str):
        """Handle meta-commands (starting with .)"""

        if cmd == '.help':
            print(__doc__)

        elif cmd == '.history':
            print(f"\n{Color.CYAN}Command History:{Color.RESET}")
            for i, hist_cmd in enumerate(self.command_history, 1):
                print(f"  {i:3}  {hist_cmd}")
            print()

        elif cmd == '.snapshots':
            snapshots = self.interpreter.time_travel.list_snapshots()
            print(f"\n{Color.CYAN}Execution Snapshots:{Color.RESET}")
            for idx, snap in snapshots:
                age = time.time() - snap.timestamp
                print(f"  [{idx:3}]  {age:6.2f}s ago  {snap}")
            print()

        elif cmd.startswith('.rewind'):
            parts = cmd.split()
            steps = int(parts[1]) if len(parts) > 1 else 1

            try:
                snap = self.interpreter.time_travel.restore(self.interpreter, -steps)
                print(f"{Color.GREEN}Rewound {steps} step(s) to {snap}{Color.RESET}\n")
            except (IndexError, ValueError) as e:
                print(f"{Color.RED}Cannot rewind: {e}{Color.RESET}\n")

        elif cmd.startswith('.save'):
            parts = cmd.split()
            if len(parts) < 2:
                print(f"{Color.RED}Usage: .save FILENAME{Color.RESET}\n")
            else:
                filename = parts[1]
                # TODO: Implement session saving
                print(f"{Color.YELLOW}Session saving not yet implemented{Color.RESET}\n")

        elif cmd.startswith('.load'):
            parts = cmd.split()
            if len(parts) < 2:
                print(f"{Color.RED}Usage: .load FILENAME{Color.RESET}\n")
            else:
                filename = parts[1]
                # TODO: Implement session loading
                print(f"{Color.YELLOW}Session loading not yet implemented{Color.RESET}\n")

        elif cmd == '.quit' or cmd == '.exit':
            self.running = False
            print(f"\n{Color.CYAN}Goodbye. Your confessions will be remembered.{Color.RESET}\n")

        else:
            print(f"{Color.RED}Unknown command: {cmd}{Color.RESET}")
            print(f"{Color.YELLOW}Type '.help' for available commands{Color.RESET}\n")

    def eval_line(self, line: str):
        """Evaluate a single line of Lament code"""

        try:
            # Lex
            lexer = Lexer(line)
            tokens = lexer.tokenize()

            # Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Execute
            if ast:
                self.interpreter.execute(ast)

        except SyntaxError as e:
            print(f"\n{Color.RED}Syntax Error: {e}{Color.RESET}\n")

        except Exception as e:
            print(f"\n{Color.RED}Error: {e}{Color.RESET}\n")

    def run(self):
        """Main REPL loop"""

        self.print_banner()

        while self.running:
            try:
                line = self.print_prompt().strip()

                if not line:
                    continue

                # Check for meta-command
                if line.startswith('.'):
                    self.handle_command(line)
                else:
                    # Execute Lament code
                    self.command_history.append(line)
                    self.eval_line(line)

            except EOFError:
                # Ctrl+D pressed
                self.running = False
                print(f"\n\n{Color.CYAN}Session ended. {len(self.interpreter.time_travel.snapshots)} snapshots captured.{Color.RESET}\n")

            except KeyboardInterrupt:
                # Ctrl+C pressed
                print(f"\n{Color.YELLOW}(Interrupted - use .quit to exit){Color.RESET}\n")


def main():
    """Entry point"""
    repl = LamentREPL()
    repl.run()


if __name__ == '__main__':
    main()
