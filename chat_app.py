import flet as ft
from datetime import datetime
import requests
import threading

class ChatApp:
    def __init__(self):
        self.messages = []
        ft.app(target=self.main)
        
    def main(self, page: ft.Page):
        # 配置页面
        page.title = "聊天应用"
        page.window_width = 400
        page.window_height = 600
        page.padding = 20
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # 创建消息列表
        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
            padding=20,
        )
        
        # 创建输入区域
        self.input_field = ft.TextField(
            expand=True,
            border_radius=30,
            filled=True,
            hint_text="输入消息...",
            on_submit=self.send_message,
            border_color=ft.colors.BLUE_400,
            bgcolor=ft.colors.WHITE,
        )
        
        # 创建发送按钮
        send_button = ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            icon_color=ft.colors.BLUE_400,
            tooltip="发送",
            on_click=self.send_message,
        )
        
        # 创建输入区域容器
        input_container = ft.Container(
            content=ft.Row(
                [
                    self.input_field,
                    send_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=20, right=20),
        )
        
        # 将所有元素添加到页面
        page.add(
            ft.Container(
                content=self.chat_list,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=10,
                expand=True,
            ),
            input_container,
        )
        
        # 添加欢迎消息
        self.add_message("系统", "欢迎使用聊天应用！", "system")
        
    def create_message_container(self, sender: str, message: str, message_type: str):
        timestamp = datetime.now().strftime("%H:%M")
        
        # 根据消息类型设置样式
        if message_type == "user":
            alignment = ft.MainAxisAlignment.END
            color = ft.colors.BLUE_400
            text_color = ft.colors.WHITE
        elif message_type == "ai":
            alignment = ft.MainAxisAlignment.START
            color = ft.colors.GREY_200
            text_color = ft.colors.BLACK
        else:  # system
            alignment = ft.MainAxisAlignment.CENTER
            color = ft.colors.GREY_300
            text_color = ft.colors.BLACK
            
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            f"{timestamp} {sender}",
                            size=12,
                            color=ft.colors.GREY_600,
                        )
                    ],
                    alignment=alignment,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                message,
                                color=text_color,
                                size=14,
                                selectable=True,
                            ),
                            bgcolor=color,
                            padding=10,
                            border_radius=10,
                            width=300,
                        )
                    ],
                    alignment=alignment,
                ),
            ],
        )
        
    def add_message(self, sender: str, message: str, message_type: str):
        self.chat_list.controls.append(
            self.create_message_container(sender, message, message_type)
        )
        self.chat_list.update()
        
    def send_message(self, e):
        message = self.input_field.value
        if message and message.strip():
            # 清空输入框
            self.input_field.value = ""
            self.input_field.update()
            
            # 显示用户消息
            self.add_message("你", message, "user")
            
            # 在新线程中获取响应
            threading.Thread(target=self.get_response, args=(message,)).start()
            
    def get_response(self, message: str):
        try:
            # API配置
            url = 'https://yuanqi.tencent.com/openapi/v1/agent/chat/completions'
            headers = {
                'X-Source': 'openapi',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer qyOABjlgZtKf9OiRSlBgkjByuSQ5DqQv'
            }
            
            # 构建请求数据
            payload = {
                "assistant_id": "gsRYqCTCelvR",
                "user_id": "user123",
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                ]
            }
            
            # 发送请求
            response = requests.post(url, headers=headers, json=payload)
            
            # 检查响应状态码
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 根据API实际返回格式提取消息
                    if 'choices' in response_data:
                        ai_message = response_data['choices'][0]['message']['content']
                        self.add_message("AI", ai_message, "ai")
                    else:
                        self.add_message("系统", "无法获取回复内容", "system")
                        
                except Exception as parse_error:
                    print(f"Parse Error: {str(parse_error)}")
                    self.add_message("系统", "解析响应时出错", "system")
            else:
                self.add_message("系统", f"请求失败: HTTP {response.status_code}", "system")
                
        except Exception as e:
            print(f"Request Error: {str(e)}")
            self.add_message("系统", "发生网络错误，请稍后重试。", "system")

if __name__ == "__main__":
    ChatApp() 