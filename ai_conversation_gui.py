import pyxel
import os
import sys
from llama_cpp import Llama
import time
import threading
import PyxelUniversalFont as puf

class ChatMessage:
    def __init__(self, speaker, content, color):
        self.speaker = speaker
        self.content = content
        self.color = color
        self.timestamp = time.time()

class AIConversationGUI:
    def __init__(self):
        # 画面設定
        self.SCREEN_WIDTH = 400
        self.SCREEN_HEIGHT = 300
        
        # 初期化
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="AI Chat Monitor")
        
        # フォント設定
        self.writer = puf.Writer("misaki_gothic.ttf")
        
        # チャット設定
        self.messages = []
        self.max_messages = 15
        self.scroll_offset = 0
        
        # AI設定
        self.ai1 = None
        self.ai2 = None
        self.conversation_history = []
        self.is_conversation_active = False
        self.current_turn = 0
        self.max_turns = 10
        
        # ペルソナ設定
        self.ai1_persona = "都内のIT企業に勤める28歳のWebデザイナー、佐藤葵さん。仕事に情熱を注ぐ一方、最近はワークライフバランスを意識し始め、週末は趣味のヨガやカフェ巡りで心身をリフレッシュしている。新しいスキルアップのために、オンライン講座にも興味を持っている。"
        self.ai2_persona = "郊外に住む45歳の会社員、鈴木誠さん。二人の子供を持つ父親で、休日は少年野球のコーチをしたり、家族でキャンプに出かけたりと、アウトドアな時間を大切にしている。最近、健康診断の結果をきっかけに、毎朝のジョギングを日課にした。"
        
        # 統計情報
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        
        # 時間計測用
        self.conversation_start_time = None
        self.conversation_end_time = None
        
        # ストリーミング表示用
        self.current_streaming_message = None
        self.streaming_content = ""

        # マウスカーソルを表示
        pyxel.mouse(True)  
        
        pyxel.run(self.update, self.draw)

    def get_resource_path(self, relative_path):
        """ 実行可能ファイル内のリソースへのパスを取得する """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def get_model_path(self, model_filename):
        """ モデルファイルのパスを取得する（常に外部ファイルとして） """
        # 実行ファイルのディレクトリを取得
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller環境では、実行ファイルのディレクトリを基準にする
            exe_dir = os.path.dirname(sys.executable)
        else:
            # 開発環境では、スクリプトのディレクトリを基準にする
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(exe_dir, "models", model_filename)

    def load_ai_models(self):
        """AIモデルを読み込む"""
        MODEL_PATH = self.get_model_path("Llama-3-ELYZA-JP-8B-Q4_K_M.gguf")
        
        # モデルファイルの存在確認
        if not os.path.exists(MODEL_PATH):
            self.add_message("エラー", f"モデルファイルが見つかりません: {MODEL_PATH}", 8)
            self.add_message("システム", "実行ファイルと同じディレクトリにmodelsフォルダを配置してください", 11)
            return False
        
        try:
            self.ai1 = Llama(
                model_path=MODEL_PATH,
                n_gpu_layers=0,  # -1でエラーが起きる場合0に設定
                n_ctx=8192,
                verbose=False,
                seed=-1,
            )
            self.ai2 = Llama(
                model_path=MODEL_PATH,
                n_gpu_layers=0,  # -1でエラーが起きる場合0に設定
                n_ctx=8192,
                verbose=False,
                seed=-1,
            )
            self.add_message("システム", "AIモデルを読み込みました", 11)
            return True
        except Exception as e:
            self.add_message("エラー", f"モデル読み込み失敗: {str(e)}", 8)
            return False

    def add_message(self, speaker, content, color):
        """メッセージを追加"""
        message = ChatMessage(speaker, content, color)
        self.messages.append(message)
        
        # メッセージ数制限
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def add_streaming_message(self, speaker, color):
        """ストリーミング用メッセージを開始"""
        self.current_streaming_message = ChatMessage(speaker, "", color)
        self.messages.append(self.current_streaming_message)
        self.streaming_content = ""
        
        # メッセージ数制限
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def update_streaming_content(self, new_content):
        """ストリーミング中のメッセージを更新"""
        if self.current_streaming_message:
            self.streaming_content += new_content
            self.current_streaming_message.content = self.streaming_content

    def finish_streaming_message(self):
        """ストリーミングを終了"""
        self.current_streaming_message = None
        self.streaming_content = ""

    def create_prompt(self, persona, conversation_history):
        """AIに渡すプロンプトを構築する関数"""
        history_text = ""
        for entry in conversation_history:
            if entry["speaker"] == "初期トピック":
                history_text += f"葵: {entry['content']}\n"
            elif entry["speaker"] == "AI1":
                history_text += f"葵: {entry['content']}\n"
            elif entry["speaker"] == "AI2":
                history_text += f"誠: {entry['content']}\n"

        prompt = f"""あなたのペルソナに従って、相手の発言に応答する発言を作成しなさい。
発言は、【これまでの会話】を踏まえて、会話の流れに沿ったものを作成しなさい。特に、相手からの質問に対しては、丁寧に答えなさい。
出力には応答のみを含め、他の情報は出力しないでください。

【あなたのペルソナ】
{persona}

【これまでの会話】
{history_text}
"""
        return prompt

    def create_end_prompt(self, persona, conversation_history):
        """会話の終了を目標にAIに渡すプロンプトを構築する関数"""
        history_text = ""
        for entry in conversation_history:
            if entry["speaker"] == "初期トピック":
                history_text += f"葵: {entry['content']}\n"
            elif entry["speaker"] == "AI1":
                history_text += f"葵: {entry['content']}\n"
            elif entry["speaker"] == "AI2":
                history_text += f"誠: {entry['content']}\n"

        prompt = f"""あなたのペルソナに従って、相手との会話を終了させるための発言を作成しなさい。
発言は、【これまでの会話】を踏まえて、会話の流れに沿って、自然に終了させることを促すものにしなさい。
出力には応答のみを含め、他の情報は出力しないでください。

【あなたのペルソナ】
{persona}

【これまでの会話】
{history_text}
"""
        return prompt

    def create_topic_prompt(self, persona):
        """初期トピックを生成するためのプロンプトを構築する関数"""
        prompt = f"""
あなたは喫茶店で誠さんに出会いました。【あなたのペルソナ】に従って、適当な話題で会話を始めてください。

【あなたのペルソナ】
{persona}
"""
        return prompt

    def start_conversation(self):
        """会話を開始"""
        if not self.ai1 or not self.ai2:
            if not self.load_ai_models():
                return
        
        self.is_conversation_active = True
        self.current_turn = 0
        self.conversation_history = []
        
        # 会話開始時刻を記録
        self.conversation_start_time = time.time()
        
        # 別スレッドで会話を実行
        conversation_thread = threading.Thread(target=self.run_conversation)
        conversation_thread.daemon = True
        conversation_thread.start()

    def run_conversation(self):
        """会話を実行（別スレッド）"""
        try:
            # 初期トピック生成
            self.add_message("システム", "初期トピックを生成中...", 11)
            topic_prompt = self.create_topic_prompt(self.ai1_persona)
            
            # ストリーミング表示で初期トピック生成
            self.add_streaming_message("トピック", 10)
            response = self.ai1.create_chat_completion(
                messages=[{"role": "user", "content": topic_prompt}],
                temperature=0.8,
                max_tokens=256,
                stream=True,  # ストリーミング有効
            )
            
            # ストリーミング処理
            full_response = ""
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        content = delta['content']
                        full_response += content
                        self.update_streaming_content(content)
                        time.sleep(0.01)  # 表示速度調整
            
            self.finish_streaming_message()
            initial_topic = full_response.strip()
            self.conversation_history.append({"speaker": "初期トピック", "content": initial_topic})
            
            current_speaker = "AI2"
            
            # 会話ループ
            for turn in range(self.max_turns):
                self.current_turn = turn
                
                if current_speaker == "AI1":
                    conv_len = len(self.conversation_history)
                    recent_history = self.conversation_history[max(0, conv_len - 5):]
                    
                    if turn < self.max_turns - 2:
                        prompt = self.create_prompt(self.ai1_persona, recent_history)
                    else:
                        prompt = self.create_end_prompt(self.ai1_persona, recent_history)
                    
                    # ストリーミング表示でAI1応答
                    self.add_streaming_message("葵", 12)
                    response = self.ai1.create_chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.4,
                        max_tokens=512,
                        stream=True,  # ストリーミング有効
                    )
                    
                    # ストリーミング処理
                    full_response = ""
                    for chunk in response:
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                full_response += content
                                self.update_streaming_content(content)
                                time.sleep(0.01)  # 表示速度調整
                    
                    self.finish_streaming_message()
                    self.conversation_history.append({"speaker": "AI1", "content": full_response})
                    current_speaker = "AI2"
                    
                else:
                    conv_len = len(self.conversation_history)
                    recent_history = self.conversation_history[max(0, conv_len - 5):]
                    
                    if turn < self.max_turns - 2:
                        prompt = self.create_prompt(self.ai2_persona, recent_history)
                    else:
                        prompt = self.create_end_prompt(self.ai2_persona, recent_history)
                    
                    # ストリーミング表示でAI2応答
                    self.add_streaming_message("誠", 14)
                    response = self.ai2.create_chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.4,
                        max_tokens=512,
                        stream=True,  # ストリーミング有効
                    )
                    
                    # ストリーミング処理
                    full_response = ""
                    for chunk in response:
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                full_response += content
                                self.update_streaming_content(content)
                                time.sleep(0.01)  # 表示速度調整
                    
                    self.finish_streaming_message()
                    self.conversation_history.append({"speaker": "AI2", "content": full_response})
                    current_speaker = "AI1"
                
                time.sleep(0.5)  # ターン間の短い休憩
            
            # 会話終了
            self.is_conversation_active = False
            
            # 会話終了時刻を記録して経過時間を計算
            self.conversation_end_time = time.time()
            elapsed_time = self.conversation_end_time - self.conversation_start_time
            
            # 統計情報を表示
            total_tokens = self.total_prompt_tokens + self.total_completion_tokens
            self.add_message("統計", f"合計トークン: {total_tokens}", 11)
            self.add_message("統計", f"経過時間: {elapsed_time:.1f}秒", 11)
            
        except Exception as e:
            self.add_message("エラー", f"会話中にエラー: {str(e)}", 8)
            self.is_conversation_active = False

    def wrap_text(self, text, max_width):
        """テキストを指定幅で折り返し（日本語対応）"""
        lines = []
        current_line = ""
        char_width = 16  # 1文字あたりの幅（ピクセル）
        max_chars = max_width // char_width
        
        for char in text:
            # 改行文字の場合
            if char == '\n':
                lines.append(current_line)
                current_line = ""
                continue
            
            # 文字を追加してみて幅をチェック
            test_line = current_line + char
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                # 現在の行を保存して新しい行を開始
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        # 最後の行を追加
        if current_line:
            lines.append(current_line)
        
        return lines

    def update(self):
        """更新処理"""
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.is_conversation_active:
            self.start_conversation()
        
        if pyxel.btnp(pyxel.KEY_UP):
            self.scroll_offset = max(0, self.scroll_offset - 1)
        
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.scroll_offset = min(len(self.messages) - 1, self.scroll_offset + 1)

    def draw(self):
        """描画処理"""
        pyxel.cls(0)
        
        # タイトル
        self.writer.draw(5, 5, "AI Chat Monitor", 16, 7)
        
        # 指示
        if not self.is_conversation_active:
            self.writer.draw(5, 20, "SPACEキーで会話開始", 16, 6)
        else:
            self.writer.draw(5, 20, f"会話中... ({self.current_turn + 1}/{self.max_turns})", 16, 6)
        
        # チャットメッセージ
        y_pos = 40
        visible_messages = self.messages[self.scroll_offset:self.scroll_offset + 8]  # 表示数を調整
        
        for message in visible_messages:
            if y_pos >= self.SCREEN_HEIGHT - 30:
                break
            
            # 発言者名
            self.writer.draw(5, y_pos, f"{message.speaker}:", 16, message.color)
            y_pos += 18
            
            # メッセージ内容（折り返し）
            wrapped_lines = self.wrap_text(message.content, self.SCREEN_WIDTH - 25)  # 余白を考慮
            for i, line in enumerate(wrapped_lines):
                if y_pos >= self.SCREEN_HEIGHT - 30 or i >= 8:  # 最大8行まで表示
                    if i >= 8 and len(wrapped_lines) > 8:
                        # 省略記号を表示
                        self.writer.draw(15, y_pos - 16, "...", 16, 7)
                    break
                self.writer.draw(15, y_pos, line, 16, 7)
                y_pos += 16
            
            y_pos += 8  # メッセージ間の間隔
        
        # スクロール情報
        self.writer.draw(5, self.SCREEN_HEIGHT - 20, "↑↓でスクロール", 16, 6)

if __name__ == "__main__":
    AIConversationGUI()
