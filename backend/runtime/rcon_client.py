from typing import List


class RCONClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

    def execute(self, command: str) -> str:
        return f"Executed: {command} (stubbed)"

    def list_players(self) -> List[str]:
        return ["player1", "player2"]
