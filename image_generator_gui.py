# coding:utf-8
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import json
import time
import requests
import base64
from volcengine import visual
from volcengine.visual.VisualService import VisualService

class ImageGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI图像生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 配置文件路径
        self.config_file = "config.json"
        
        # 配置变量
        self.ak = tk.StringVar()
        self.sk = tk.StringVar()
        self.save_dir = tk.StringVar(value="generated_images")
        self.aspect_ratio = tk.StringVar(value="1:1")
        self.custom_width = tk.StringVar(value="1024")
        self.custom_height = tk.StringVar(value="1024")
        
        # 默认提示词
        self.default_prompt = "标题：试错，副标题：才是产品经理的常态，特写：一个产品经理正在思考那些犯过的错，背景：各种PPT、图表、报表，要求：背景模糊处理，标题清晰醒目，用海报设计字体"
        
        # 加载保存的配置
        self.load_config()
        
        self.setup_ui()
        
        # 程序关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def simple_encrypt(self, text):
        """简单的文本加密（Base64编码）"""
        if not text:
            return ""
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception:
            return text
    
    def simple_decrypt(self, encoded_text):
        """简单的文本解密（Base64解码）"""
        if not encoded_text:
            return ""
        try:
            decoded = base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
            return decoded
        except Exception:
            return encoded_text
    
    def load_config(self):
        """从配置文件加载设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 解密并设置API密钥
                if 'ak' in config:
                    self.ak.set(self.simple_decrypt(config['ak']))
                if 'sk' in config:
                    self.sk.set(self.simple_decrypt(config['sk']))
                
                # 设置保存目录
                if 'save_dir' in config:
                    self.save_dir.set(config['save_dir'])
                
                # 设置图片比例
                if 'aspect_ratio' in config:
                    self.aspect_ratio.set(config['aspect_ratio'])
                if 'custom_width' in config:
                    self.custom_width.set(config['custom_width'])
                if 'custom_height' in config:
                    self.custom_height.set(config['custom_height'])
                    
                print("配置加载成功")
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存设置到配置文件"""
        try:
            config = {
                'ak': self.simple_encrypt(self.ak.get()),
                'sk': self.simple_encrypt(self.sk.get()),
                'save_dir': self.save_dir.get(),
                'aspect_ratio': self.aspect_ratio.get(),
                'custom_width': self.custom_width.get(),
                'custom_height': self.custom_height.get()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            print("配置保存成功")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def on_closing(self):
        """程序关闭时的处理"""
        self.save_config()
        self.root.destroy()
    
    def browse_directory(self):
        """浏览并选择保存目录"""
        directory = filedialog.askdirectory(initialdir=self.save_dir.get())
        if directory:
            self.save_dir.set(directory)
            # 目录改变时自动保存配置
            self.save_config()
    
    def get_image_dimensions(self):
        """根据选择的比例返回图片尺寸"""
        ratio = self.aspect_ratio.get()
        
        # 预设比例对应的尺寸（基于1024像素）
        ratio_dimensions = {
            "1:1": (1024, 1024),
            "2:3": (683, 1024),
            "4:3": (1024, 768),
            "9:16": (576, 1024),
            "16:9": (1024, 576),
            "16:7": (1024, 448)
        }
        
        if ratio == "自定义":
            try:
                width = max(500, int(self.custom_width.get()))
                height = max(500, int(self.custom_height.get()))
                return (width, height)
            except ValueError:
                # 如果输入无效，返回默认尺寸
                return (1024, 1024)
        else:
            return ratio_dimensions.get(ratio, (1024, 1024))
    
    def on_aspect_ratio_change(self):
        """比例选择改变时的处理"""
        if self.aspect_ratio.get() == "自定义":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()
        
        # 更新尺寸显示
        width, height = self.get_image_dimensions()
        self.dimension_label.config(text=f"图片尺寸: {width} × {height}")
        
        # 自动保存配置
        self.save_config()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # API密钥配置区域
        config_frame = ttk.LabelFrame(main_frame, text="API配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="Access Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ak_entry = ttk.Entry(config_frame, textvariable=self.ak, width=50, show="*")
        ak_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(config_frame, text="Secret Key:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        sk_entry = ttk.Entry(config_frame, textvariable=self.sk, width=50, show="*")
        sk_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # 保存目录配置
        ttk.Label(config_frame, text="保存目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        dir_frame = ttk.Frame(config_frame)
        dir_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        dir_frame.columnconfigure(0, weight=1)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.save_dir)
        dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="浏览", command=self.browse_directory).grid(row=0, column=1)
        
        # 保存配置按钮
        save_config_btn = ttk.Button(config_frame, text="保存配置", command=self.save_config)
        save_config_btn.grid(row=3, column=1, sticky=tk.E, pady=(10, 0))
        
        # 图片比例设置区域
        ratio_frame = ttk.LabelFrame(main_frame, text="图片比例设置", padding="10")
        ratio_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ratio_frame.columnconfigure(1, weight=1)
        
        ttk.Label(ratio_frame, text="比例:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # 比例选择下拉框
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.aspect_ratio, 
                                  values=["1:1", "2:3", "4:3", "9:16", "16:9", "16:7", "自定义"],
                                  state="readonly", width=15)
        ratio_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ratio_combo.bind('<<ComboboxSelected>>', lambda e: self.on_aspect_ratio_change())
        
        # 尺寸显示标签
        width, height = self.get_image_dimensions()
        self.dimension_label = ttk.Label(ratio_frame, text=f"图片尺寸: {width} × {height}")
        self.dimension_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # 自定义尺寸输入框（初始隐藏）
        self.custom_frame = ttk.Frame(ratio_frame)
        self.custom_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(self.custom_frame, text="宽度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        width_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_width, width=8)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        width_entry.bind('<KeyRelease>', lambda e: self.on_custom_size_change())
        
        ttk.Label(self.custom_frame, text="高度:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        height_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_height, width=8)
        height_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        height_entry.bind('<KeyRelease>', lambda e: self.on_custom_size_change())
        
        ttk.Label(self.custom_frame, text="(最小500像素)", 
                 foreground="gray").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        
        # 初始隐藏自定义框
        if self.aspect_ratio.get() != "自定义":
            self.custom_frame.grid_remove()
        
        # 提示词输入区域
        prompt_frame = ttk.LabelFrame(main_frame, text="提示词", padding="10")
        prompt_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        
        # 默认提示词按钮
        button_frame = ttk.Frame(prompt_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(button_frame, text="使用默认提示词", command=self.load_default_prompt).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="清空", command=self.clear_prompt).pack(side=tk.LEFT, padx=(5, 0))
        
        # 提示词文本框
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD)
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.prompt_text.insert(tk.END, self.default_prompt)
        
        # 生成按钮
        self.generate_button = ttk.Button(main_frame, text="生成图像", command=self.start_generation)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的行权重
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def load_default_prompt(self):
        """加载默认提示词"""
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(tk.END, self.default_prompt)
        
    def clear_prompt(self):
        """清空提示词"""
        self.prompt_text.delete(1.0, tk.END)
    
    def on_custom_size_change(self):
        """自定义尺寸输入改变时的处理"""
        try:
            width = max(500, int(self.custom_width.get()))
            height = max(500, int(self.custom_height.get()))
            self.dimension_label.config(text=f"图片尺寸: {width} × {height}")
        except ValueError:
            # 如果输入无效，显示默认值
            self.dimension_label.config(text="图片尺寸: 请输入有效数值")
        
        # 延迟保存配置，避免频繁保存
        self.root.after(1000, self.save_config)
        
    def log_message(self, message):
        """在状态文本框中显示消息"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def download_image(self, url, save_path):
        """下载图片并保存到本地"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            self.log_message(f"图片已保存到: {save_path}")
            return True
        except Exception as e:
            self.log_message(f"下载图片失败: {str(e)}")
            return False
            
    def generate_image(self, visual_service, prompt):
        """提交图像生成任务并返回task_id"""
        # 获取图片尺寸
        width, height = self.get_image_dimensions()
        
        submit_form = {
            "req_key": "jimeng_t2i_v31",
            "prompt": prompt,
            "seed": -5,
            "width": width,
            "height": height
        }
        
        self.log_message(f"正在提交图像生成任务... (尺寸: {width}×{height})")
        submit_resp = visual_service.cv_sync2async_submit_task(submit_form)
        
        if submit_resp.get("code") != 10000:
            self.log_message(f"提交任务失败: {json.dumps(submit_resp, ensure_ascii=False)}")
            return None
        
        task_id = submit_resp["data"].get("task_id")
        if not task_id:
            self.log_message("获取任务ID失败")
            return None
        
        self.log_message(f"任务已提交，ID: {task_id}")
        return task_id
        
    def get_image_result(self, visual_service, task_id):
        """查询任务结果并返回图片URL列表"""
        result_form = {
            "req_key": "jimeng_t2i_v31",
            "task_id": task_id,
            "req_json": json.dumps({
                "logo_info": {
                    "add_logo": False,
                    "position": 0,
                    "language": 0,
                    "opacity": 0.3,
                    "logo_text_content": "这里是明水印内容"
                },
                "return_url": True
            })
        }
        
        max_retries = 20
        retry_interval = 5
        
        for i in range(max_retries):
            self.log_message(f"正在查询结果({i+1}/{max_retries})...")
            result_resp = visual_service.cv_sync2async_get_result(result_form)
            
            if result_resp.get("code") == 10000:
                status = result_resp["data"].get("status", "")
                
                if status == "done":
                    self.log_message("任务处理完成")
                    return result_resp["data"].get("image_urls", [])
                elif status == "failed":
                    self.log_message("任务处理失败")
                    return []
                elif status in ["pending", "processing"]:
                    self.log_message(f"任务处理中，状态: {status}")
                else:
                    self.log_message(f"未知状态: {status}")
            else:
                self.log_message(f"查询结果失败: {json.dumps(result_resp, ensure_ascii=False)}")
                return []
            
            time.sleep(retry_interval)
        
        self.log_message("任务处理超时")
        return []
        
    def generation_worker(self):
        """图像生成工作线程"""
        try:
            # 验证输入
            ak = self.ak.get().strip()
            sk = self.sk.get().strip()
            prompt = self.prompt_text.get(1.0, tk.END).strip()
            
            if not ak or not sk:
                messagebox.showerror("错误", "请填写Access Key和Secret Key")
                return
                
            if not prompt:
                messagebox.showerror("错误", "请输入提示词")
                return
            
            # 创建保存目录
            save_dir = self.save_dir.get()
            os.makedirs(save_dir, exist_ok=True)
            
            # 初始化服务
            visual_service = VisualService()
            visual_service.set_ak(ak)
            visual_service.set_sk(sk)
            
            # 提交任务
            task_id = self.generate_image(visual_service, prompt)
            if not task_id:
                return
            
            # 获取结果
            image_urls = self.get_image_result(visual_service, task_id)
            
            # 下载图片
            if image_urls:
                for idx, url in enumerate(image_urls):
                    filename = f"{task_id}_{idx}.jpg"
                    save_path = os.path.join(save_dir, filename)
                    self.log_message(f"正在下载图片 {idx+1}/{len(image_urls)}: {url}")
                    self.download_image(url, save_path)
                    
                self.log_message(f"所有图片已保存完成！共{len(image_urls)}张图片")
                messagebox.showinfo("完成", f"图像生成完成！共生成{len(image_urls)}张图片")
            else:
                self.log_message("未获取到图片URL或任务失败")
                messagebox.showerror("失败", "图像生成失败，请检查日志信息")
                
        except Exception as e:
            error_msg = f"生成过程中发生错误: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("错误", error_msg)
        finally:
            # 恢复按钮状态
            self.generate_button.config(state=tk.NORMAL, text="生成图像")
            self.progress.stop()
            
    def start_generation(self):
        """开始图像生成"""
        # 禁用生成按钮
        self.generate_button.config(state=tk.DISABLED, text="生成中...")
        self.progress.start()
        
        # 清空状态日志
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # 在新线程中执行生成任务
        thread = threading.Thread(target=self.generation_worker)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = ImageGeneratorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()