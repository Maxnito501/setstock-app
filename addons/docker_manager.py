"""
Docker Manager - จัดการ Docker container สำหรับ Settrade API
"""

import subprocess
import os
import json
import time
import requests

class DockerManager:
    """จัดการ Docker container"""
    
    def __init__(self, container_name='settrade-api', port=5001):
        self.container_name = container_name
        self.port = port
        self.service_url = f"http://localhost:{port}"
        
    def check_docker_installed(self):
        """ตรวจสอบว่ามี Docker หรือไม่"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                   capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_container_running(self):
        """ตรวจสอบว่า container กำลังทำงานอยู่หรือไม่"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.container_name}', 
                 '--format', '{{.Names}}'],
                capture_output=True, text=True
            )
            return self.container_name in result.stdout
        except:
            return False
    
    def check_service_ready(self):
        """ตรวจสอบว่า service พร้อมใช้งาน"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_container(self, build=False):
        """เริ่มต้น Docker container"""
        if not self.check_docker_installed():
            return {
                'success': False,
                'error': 'Docker not installed'
            }
        
        if self.check_container_running():
            if self.check_service_ready():
                return {
                    'success': True,
                    'message': 'Container already running',
                    'url': self.service_url
                }
        
        try:
            if build:
                # สร้าง image ใหม่
                subprocess.run([
                    'docker', 'build', '-t', self.container_name,
                    '-f', 'docker/Dockerfile.settrade', '.'
                ], check=True)
            
            # รัน container
            subprocess.run([
                'docker', 'run', '-d',
                '--name', self.container_name,
                '-p', f'{self.port}:5000',
                '--restart', 'unless-stopped',
                self.container_name
            ], check=True)
            
            # รอให้ service พร้อม
            for _ in range(10):
                time.sleep(2)
                if self.check_service_ready():
                    return {
                        'success': True,
                        'message': 'Container started',
                        'url': self.service_url
                    }
            
            return {
                'success': False,
                'error': 'Service not ready'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_container(self):
        """หยุด Docker container"""
        try:
            subprocess.run(['docker', 'stop', self.container_name], check=True)
            subprocess.run(['docker', 'rm', self.container_name], check=True)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_container_status(self):
        """ดูสถานะ container"""
        status = {
            'docker_installed': self.check_docker_installed(),
            'container_running': self.check_container_running(),
            'service_ready': self.check_service_ready() if self.check_container_running() else False,
            'url': self.service_url
        }
        return status
