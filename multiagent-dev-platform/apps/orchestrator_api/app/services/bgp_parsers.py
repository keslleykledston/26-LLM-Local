"""
Parsers for BGP peer/summary outputs across vendors
"""
from typing import List, Dict
import re


def parse_huawei_bgp_peer(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    started = False
    for line in text.splitlines():
        if re.match(r"\s*Peer\s+V\s+AS\s+MsgRcvd", line):
            started = True
            continue
        if not started:
            continue
        if not line.strip():
            continue

        match = re.match(
            r"^\s*(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$",
            line,
        )
        if not match:
            continue

        peer, _version, asn, rcvd, sent, outq, updown, state, pref = match.groups()
        rows.append(
            {
                "peer": peer,
                "as": asn,
                "msg_rcvd": rcvd,
                "msg_sent": sent,
                "outq": outq,
                "up_down": updown,
                "state": state,
                "pref_rcv": pref,
            }
        )
    return rows


def _parse_state_pfx(value: str) -> Dict[str, str]:
    if value.isdigit():
        return {"state": "Established", "pref_rcv": value}
    return {"state": value, "pref_rcv": ""}


def parse_cisco_bgp_summary(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.strip().startswith("Neighbor"):
            continue
        if not re.match(r"^\s*\d+\.\d+\.\d+\.\d+\s+", line):
            continue

        parts = line.split()
        if len(parts) < 9:
            continue

        neighbor = parts[0]
        asn = parts[2]
        rcvd = parts[3]
        sent = parts[4]
        outq = parts[7]
        updown = parts[8]
        state_pfx = parts[9] if len(parts) > 9 else ""
        state_info = _parse_state_pfx(state_pfx)

        rows.append(
            {
                "peer": neighbor,
                "as": asn,
                "msg_rcvd": rcvd,
                "msg_sent": sent,
                "outq": outq,
                "up_down": updown,
                "state": state_info["state"],
                "pref_rcv": state_info["pref_rcv"],
            }
        )
    return rows


def parse_juniper_bgp_summary(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if line.strip().startswith("Peer"):
            continue
        if not re.match(r"^\s*\d+\.\d+\.\d+\.\d+\s+", line):
            continue

        parts = line.split()
        if len(parts) < 7:
            continue

        neighbor = parts[0]
        asn = parts[1]
        rcvd = parts[2]
        sent = parts[3]
        outq = parts[4]
        updown = parts[6] if len(parts) > 6 else ""
        state_field = parts[7] if len(parts) > 7 else ""
        state, pref = state_field, ""
        if "|" in state_field:
            state, pref = state_field.split("|", 1)

        rows.append(
            {
                "peer": neighbor,
                "as": asn,
                "msg_rcvd": rcvd,
                "msg_sent": sent,
                "outq": outq,
                "up_down": updown,
                "state": state,
                "pref_rcv": pref,
            }
        )
    return rows


def parse_mikrotik_bgp(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if "remote" not in line and "state=" not in line:
            continue

        pairs = dict(re.findall(r"([\\w\\.-]+)=([^\\s]+)", line))
        if not pairs:
            continue

        peer = pairs.get("remote-address") or pairs.get("remote.address")
        asn = pairs.get("remote-as") or pairs.get("remote.as")
        rcvd = (
            pairs.get("remote-messages-received")
            or pairs.get("remote.messages-received")
            or pairs.get("messages-received")
            or ""
        )
        sent = (
            pairs.get("remote-messages-sent")
            or pairs.get("remote.messages-sent")
            or pairs.get("messages-sent")
            or ""
        )
        updown = pairs.get("uptime") or pairs.get("up-time") or ""
        state = pairs.get("state") or ""

        rows.append(
            {
                "peer": peer or "",
                "as": asn or "",
                "msg_rcvd": rcvd,
                "msg_sent": sent,
                "outq": pairs.get("outq", ""),
                "up_down": updown,
                "state": state,
                "pref_rcv": pairs.get("prefix-count", ""),
            }
        )
    return rows
