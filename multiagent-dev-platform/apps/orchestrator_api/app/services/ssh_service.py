"""
SSH service for executing network commands using Netmiko
"""
from typing import List, Dict
import asyncio
from loguru import logger
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException


class SSHService:
    """Execute commands on network devices via SSH (Netmiko)"""

    def __init__(self) -> None:
        self.default_timeout = 20

    @staticmethod
    def platform_to_device_type(platform: str) -> str:
        mapping = {
            "huawei": "huawei",
            "cisco_ios": "cisco_ios",
            "cisco_xe": "cisco_ios",
            "cisco_xr": "cisco_xr",
            "juniper": "juniper_junos",
            "mikrotik_v6": "mikrotik_routeros",
            "mikrotik_v7": "mikrotik_routeros",
        }
        return mapping.get(platform, "")

    @staticmethod
    def platform_commands(platform: str) -> List[str]:
        if platform == "huawei":
            return ["screen-length 0 temporary", "display bgp peer"]
        if platform in {"cisco_ios", "cisco_xe"}:
            return ["terminal length 0", "show ip bgp summary"]
        if platform == "cisco_xr":
            return ["terminal length 0", "show bgp ipv4 unicast summary"]
        if platform == "juniper":
            return ["set cli screen-length 0", "show bgp summary"]
        if platform == "mikrotik_v6":
            return [
                "/routing bgp peer print terse proplist=remote-address,remote-as,remote-messages-received,remote-messages-sent,updates-sent,updates-received,state,uptime"
            ]
        if platform == "mikrotik_v7":
            return [
                "/routing/bgp/session/print terse proplist=remote.address,remote.as,remote.messages-received,remote.messages-sent,state,uptime"
            ]
        return []

    async def run_commands(
        self,
        *,
        platform: str,
        host: str,
        port: int,
        username: str,
        password: str,
        enable_password: str = "",
    ) -> str:
        return await asyncio.to_thread(
            self._run_commands_sync,
            platform=platform,
            host=host,
            port=port,
            username=username,
            password=password,
            enable_password=enable_password,
        )

    def _run_commands_sync(
        self,
        *,
        platform: str,
        host: str,
        port: int,
        username: str,
        password: str,
        enable_password: str = "",
    ) -> str:
        device_type = self.platform_to_device_type(platform)
        if not device_type:
            raise ValueError(f"Unsupported platform: {platform}")

        commands = self.platform_commands(platform)
        if not commands:
            raise ValueError(f"No commands configured for platform: {platform}")

        try:
            conn = ConnectHandler(
                device_type=device_type,
                host=host,
                port=port,
                username=username,
                password=password,
                conn_timeout=self.default_timeout,
                timeout=self.default_timeout,
                fast_cli=False,
            )

            if enable_password:
                conn.secret = enable_password
                try:
                    if not conn.check_enable_mode():
                        conn.enable()
                except Exception as exc:
                    logger.warning(f"Enable mode failed: {exc}")

            output = ""
            for cmd in commands:
                output = conn.send_command(cmd, strip_prompt=False, strip_command=False)

            conn.disconnect()
            return output
        except (NetmikoTimeoutException, NetmikoAuthenticationException) as exc:
            raise RuntimeError(str(exc)) from exc
