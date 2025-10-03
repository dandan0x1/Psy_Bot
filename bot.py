#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import time
import datetime
import logging
import signal
import sys
from urllib.parse import urlparse
from threading import Thread
from colorama import *

# 版权
def show_copyright():
    """展示版权信息"""
    copyright_info = f"""{Fore.CYAN}
    *****************************************************
    *           X:https://x.com/ariel_sands_dan         *
    *           Tg:https://t.me/sands0x1                *
    *           PSY BOT Version 1.0                    *
    *           Copyright (c) 2025                      *
    *           All Rights Reserved                     *
    *****************************************************
    """
    {Style.RESET_ALL}
    print(copyright_info)
    print('=' * 50)
    print(f"{Fore.GREEN}申请key: https://661100.xyz/ {Style.RESET_ALL}")
    print(f"{Fore.RED}联系Dandan: \n QQ:712987787 QQ群:1036105927 \n 电报:sands0x1 电报群:https://t.me/+fjDjBiKrzOw2NmJl \n 微信: dandan0x1{Style.RESET_ALL}")
    print('=' * 50)

# 颜色代码
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# 硬编码的User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
]


def color_print(text, color=Colors.WHITE, bold=False):
    """彩色打印函数"""
    style = Colors.BOLD if bold else ''
    print(f"{style}{color}{text}{Colors.END}")


def color_input(prompt, color=Colors.CYAN):
    """彩色输入函数"""
    style = Colors.BOLD
    return input(f"{style}{color}{prompt}{Colors.END}")


class CheckinScheduler:
    """签到调度器"""
    
    def __init__(self):
        self.running = False
        self.last_checkin_time = None
        self.current_user_agent = None
        self.setup_logging()
        self.select_user_agent()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('config/checkin.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def select_user_agent(self):
        """选择User-Agent"""
        import random
        self.current_user_agent = random.choice(USER_AGENTS)
        #self.logger.info(f"选择的User-Agent: {self.current_user_agent[:50]}...")
    
    def load_token(self):
        """从token.txt文件加载认证token"""
        token_file = 'config/token.txt'
        if not os.path.exists(token_file):
            self.logger.error(f"找不到 {token_file} 文件")
            return None
        
        with open(token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        
        if not token:
            self.logger.error("token.txt 文件为空")
            return None
        
        return token
    
    def load_proxy(self):
        """从proxy.txt文件加载代理配置"""
        proxy_file = 'config/proxy.txt'
        if not os.path.exists(proxy_file):
            return None
        
        with open(proxy_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            # 跳过注释行和空行
            if line and not line.startswith('#'):
                return line
        
        return None
    
    def checkin(self):
        """执行签到操作"""
        # 加载token
        token = self.load_token()
        if not token:
            return False
        
        # 加载代理
        proxy_url = self.load_proxy()
        proxies = None
        if proxy_url:
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            self.logger.info(f"使用代理：{proxy_url}")
        
        # 请求URL
        url = 'https://member-api.psy.xyz/tasks/check-in'
        
        # 请求头（使用硬编码的User-Agent）
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {token}',
            'content-length': '0',
            'origin': 'https://psy.xyz',
            'priority': 'u=1, i',
            'referer': 'https://psy.xyz/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.current_user_agent
        }
        
        try:
            self.logger.info("正在执行签到...")
            response = requests.post(url, headers=headers, proxies=proxies, timeout=30)
            
            self.logger.info(f"响应状态码：{response.status_code}")
            self.logger.info(f"响应内容：{response.text}")
            
            if response.status_code == 200:
                color_print("✅ 签到成功！", Colors.GREEN, bold=True)
                self.logger.info("签到成功")
                self.last_checkin_time = datetime.datetime.now()
                return True
            elif response.status_code == 400:
                # 检查是否是"已经签到"的错误
                response_data = response.json() if response.text else {}
                msg = response_data.get('msg', '')
                if 'Already checked in today' in msg or '已经签到' in msg:
                    color_print("ℹ️ 今日已签到，无需重复签到", Colors.YELLOW, bold=True)
                    self.logger.info("今日已签到，无需重复签到")
                    self.last_checkin_time = datetime.datetime.now()
                    return True
                else:
                    color_print(f"❌ 签到失败：{msg}", Colors.RED, bold=True)
                    self.logger.error(f"签到失败：{msg}")
                    return False
            else:
                color_print(f"❌ 签到失败，状态码：{response.status_code}", Colors.RED, bold=True)
                self.logger.error(f"签到失败，状态码：{response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            color_print(f"❌ 请求失败：{e}", Colors.RED, bold=True)
            self.logger.error(f"请求失败：{e}")
            return False
    
    def calculate_next_run_time(self):
        """计算下次运行时间"""
        now = datetime.datetime.now()
        if self.last_checkin_time:
            # 如果已经签到过，计算24小时后
            next_run = self.last_checkin_time + datetime.timedelta(hours=24)
            # 如果下次运行时间已过，则立即运行
            if next_run <= now:
                return now
            return next_run
        else:
            # 如果从未签到，立即运行
            return now
    
    def run_once(self):
        """运行一次签到"""
        success = self.checkin()
        if success:
            color_print("🎉 签到完成！", Colors.GREEN, bold=True)
            self.logger.info("签到完成")
        else:
            color_print("💥 签到失败，请检查网络连接和token配置", Colors.RED, bold=True)
            self.logger.error("签到失败，请检查网络连接和token配置")
        return success
    
    def run_scheduler(self):
        """运行调度器"""
        self.running = True
        self.logger.info("签到调度器启动")
        
        while self.running:
            try:
                next_run_time = self.calculate_next_run_time()
                now = datetime.datetime.now()
                
                if next_run_time <= now:
                    # 立即执行签到
                    self.logger.info("开始执行签到任务...")
                    success = self.run_once()
                    
                    if success:
                        # 签到成功或已签到，计算下次运行时间
                        next_run_time = self.calculate_next_run_time()
                        wait_seconds = (next_run_time - datetime.datetime.now()).total_seconds()
                        
                        if wait_seconds > 0:
                            self.logger.info(f"下次签到时间：{next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            self.logger.info(f"等待 {wait_seconds:.0f} 秒（约 {wait_seconds/3600:.1f} 小时）...")
                            
                            # 分段等待，以便能够响应停止信号
                            while wait_seconds > 0 and self.running:
                                sleep_time = min(60, wait_seconds)  # 最多等待60秒
                                time.sleep(sleep_time)
                                wait_seconds -= sleep_time
                        else:
                            self.logger.info("准备进行下次签到...")
                    else:
                        # 签到失败，等待5分钟后重试
                        self.logger.info("签到失败，5分钟后重试...")
                        time.sleep(300)  # 等待5分钟
                else:
                    # 等待到下次执行时间
                    wait_seconds = (next_run_time - now).total_seconds()
                    self.logger.info(f"下次签到时间：{next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    self.logger.info(f"等待 {wait_seconds:.0f} 秒（约 {wait_seconds/3600:.1f} 小时）...")
                    
                    # 分段等待，以便能够响应停止信号
                    while wait_seconds > 0 and self.running:
                        sleep_time = min(60, wait_seconds)  # 最多等待60秒
                        time.sleep(sleep_time)
                        wait_seconds -= sleep_time
                
            except KeyboardInterrupt:
                self.logger.info("收到中断信号，正在停止...")
                break
            except Exception as e:
                self.logger.error(f"调度器运行时出错：{e}")
                time.sleep(60)  # 出错后等待1分钟再重试
        
        self.logger.info("签到调度器已停止")
    
    def stop(self):
        """停止调度器"""
        self.running = False


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到停止信号，正在退出...")
    sys.exit(0)


def show_menu():
    """显示菜单"""
    print()
    color_print("PSY.xyz 签到脚本 - 24小时定时版本", Colors.CYAN, bold=True)
    color_print("=" * 50, Colors.CYAN)
    color_print("请选择运行模式：", Colors.WHITE, bold=True)
    color_print("1) 单次运行（立即签到一次）", Colors.GREEN)
    color_print("2) 定时运行（24小时循环）", Colors.YELLOW)
    color_print("3) 退出程序", Colors.RED)
    color_print("=" * 50, Colors.CYAN)

def main():
    """主函数"""
    show_copyright()
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    scheduler = CheckinScheduler()
    
    while True:
        show_menu()
        
        try:
            choice = color_input("请输入选项 (1-3): ").strip()
            
            if choice == '1':
                # 单次运行模式
                color_print("\n单次运行模式", Colors.GREEN, bold=True)
                color_print("-" * 30, Colors.GREEN)
                success = scheduler.run_once()
                input("\n按回车键返回主菜单...")
                
            elif choice == '2':
                # 定时运行模式
                color_print("\n定时运行模式启动", Colors.YELLOW, bold=True)
                color_print("-" * 30, Colors.YELLOW)
                color_print("程序将在后台运行，按Ctrl+C停止", Colors.WHITE)
                color_print("日志文件：checkin.log", Colors.CYAN)
                print("")
                try:
                    scheduler.run_scheduler()
                except KeyboardInterrupt:
                    scheduler.stop()
                    color_print("\n程序已停止", Colors.RED, bold=True)
                    input("\n按回车键返回主菜单...")
                
            elif choice == '3':
                # 退出程序
                color_print("\n感谢使用，再见！", Colors.GREEN, bold=True)
                break
                
            else:
                color_print("\n❌ 无效选项，请输入1-3之间的数字", Colors.RED, bold=True)
                input("按回车键继续...")
                
        except KeyboardInterrupt:
            color_print("\n\n程序已退出", Colors.RED, bold=True)
            break
        except Exception as e:
            color_print(f"\n❌ 程序出错：{e}", Colors.RED, bold=True)
            input("按回车键继续...")


if __name__ == "__main__":
    main()
