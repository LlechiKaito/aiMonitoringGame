import pyxel
import os
import sys
import time
import threading
import PyxelUniversalFont as puf
from dotenv import load_dotenv
import google.generativeai as genai

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
        
        # .envからAPIキーを読み込む
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Gemini APIの初期設定 (ここからが修正部分)
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # モデルの初期化
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash',
                generation_config=genai.types.GenerationConfig(
                    # temperatureやmax_output_tokensのデフォルト値をここで設定可能
                )
            )
        else:
            self.model = None

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

    # gemini_generate 関数を丸ごと置き換え
    def gemini_generate(self, prompt, stream=False, max_tokens=512, temperature=0.4):
        """Gemini APIでテキスト生成 (SDK版)"""
        if not self.model:
            yield "[エラー: Geminiモデルが初期化されていません]"
            return

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        try:
            # stream=True でストリーミングレスポンスを取得
            response_stream = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )

            # ストリーミングデータを処理
            if stream:
                for chunk in response_stream:
                    # APIからの空の応答や安全でないコンテンツをチェック
                    if chunk.parts:
                        yield chunk.text
                    else:
                        # 会話が途切れないように、安全でない場合も何らかのテキストを返す
                        yield "[内容がブロックされました]"
                        break 
            else:
                # ストリーミングでない場合（今回は使われないが念のため実装）
                full_response = ""
                for chunk in response_stream:
                     if chunk.parts:
                        full_response += chunk.text
                yield full_response

        except Exception as e:
            # 詳細なエラーメッセージを返す
            yield f"[Gemini APIエラー: {str(e)}]"

    def load_ai_models(self):
        """AIモデルのロード状況を確認"""
        if not self.gemini_api_key or not self.model:
            self.add_message("エラー", "Gemini APIキー未設定かモデル初期化失敗", 8)
            return False
        self.add_message("システム", "Gemini Proモデルを使用します", 11)
        return True

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

        prompt = f"""あなたのペルソナに従って、相手の発言に応答する発言を端的に作成しなさい。
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
あなたは喫茶店で誠さんに出会いました。【あなたのペルソナ】に従って、適当な話題で会話を始めてください。発言は端的にしなさい。

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
            response = self.gemini_generate(topic_prompt, stream=True, max_tokens=256, temperature=0.8)
            full_response = ""
            for chunk in response:
                full_response += chunk
                self.update_streaming_content(chunk)
            self.finish_streaming_message()
            initial_topic = full_response.strip()
            self.conversation_history.append({"speaker": "初期トピック", "content": initial_topic})
            
            current_speaker = "AI2"
            
            # 会話ループ
            for turn in range(self.max_turns):
                self.current_turn = turn
                conv_len = len(self.conversation_history)
                recent_history = self.conversation_history[max(0, conv_len - 5):]
                if current_speaker == "AI1":
                    if turn < self.max_turns - 2:
                        prompt = self.create_prompt(self.ai1_persona, recent_history)
                    else:
                        prompt = self.create_end_prompt(self.ai1_persona, recent_history)
                    self.add_streaming_message("葵", 12)
                    response = self.gemini_generate(prompt, stream=True, max_tokens=512, temperature=0.4)
                    full_response = ""
                    for chunk in response:
                        full_response += chunk
                        self.update_streaming_content(chunk)
                    self.finish_streaming_message()
                    self.conversation_history.append({"speaker": "AI1", "content": full_response})
                    current_speaker = "AI2"
                else:
                    if turn < self.max_turns - 2:
                        prompt = self.create_prompt(self.ai2_persona, recent_history)
                    else:
                        prompt = self.create_end_prompt(self.ai2_persona, recent_history)
                    self.add_streaming_message("誠", 14)
                    response = self.gemini_generate(prompt, stream=True, max_tokens=512, temperature=0.4)
                    full_response = ""
                    for chunk in response:
                        full_response += chunk
                        self.update_streaming_content(chunk)
                    self.finish_streaming_message()
                    self.conversation_history.append({"speaker": "AI2", "content": full_response})
                    current_speaker = "AI1"
                time.sleep(0.5)
            
            self.is_conversation_active = False
            self.conversation_end_time = time.time()
            elapsed_time = self.conversation_end_time - self.conversation_start_time
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
