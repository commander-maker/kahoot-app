import customtkinter as ctk
import threading
import socket
import queue
import queue
class ServerWindow(ctk.CTkToplevel):

    def __init__(self, parent, session_name, clients=None, initial_scores = None):
        super().__init__(parent)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.session_name = session_name
        self.parent = parent
        self.clients = clients if clients else []
        self.scores = dict(initial_scores) if initial_scores else {}  # name -> score
        self.client_names = {}  # socket -> name
        self.current_correct = None
        self.clients_lock = threading.Lock()
        self.clients_listen = set()
        self.message_queuw = queue.Queue
        self.geometry("360x540")
        self.title(f"{session_name}-kahoot Server")
        
        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=0, pady=0)
        
        tab_Session = tabs.add("Session")
        tab_Leaderbord = tabs.add("Leaderboard")
        tab_questions = tabs.add("Questions")

        # --- SESSION TAB ---
        frame = ctk.CTkFrame(master=tab_Session)
        frame.pack(fill="both", expand=True)

        top_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        top_row.pack(pady=(4, 10), padx=0, fill="x")

        label1 = ctk.CTkLabel(master=top_row, text=f"{session_name}", font=("Roboto", 24))
        label1.pack(pady=12, padx=10, side="left")

        leaderboardbtn = ctk.CTkButton(master=top_row, text="End Session", command=self.go_back)
        leaderboardbtn.pack(pady=12, padx=10, side="right")

        label2 = ctk.CTkLabel(master=frame, text="Questions")
        label2.pack(pady=(12, 2), padx=10, anchor="w")

        HEADER = 64
        PORT = 5050
        FORMAT = 'utf-8'
        SERVER = socket.gethostbyname(socket.gethostname())
        
        self.HEADER = HEADER
        self.FORMAT = FORMAT

        entry1 = ctk.CTkEntry(master=frame, placeholder_text="Question", height=32)
        entry1.pack(pady=(0, 10), padx=10, fill="x")

        label3 = ctk.CTkLabel(master=frame, text="Answers")
        label3.pack(pady=0, padx=10, anchor="w")

        answer1 = ctk.CTkEntry(master=frame, placeholder_text="Answer 1", height=32)
        answer1.pack(pady=(0, 10), padx=10, fill="x")

        answer2 = ctk.CTkEntry(master=frame, placeholder_text="Answer 2", height=32)
        answer2.pack(pady=(0, 10), padx=10, fill="x")

        answer3 = ctk.CTkEntry(master=frame, placeholder_text="Answer 3", height=32)
        answer3.pack(pady=(0, 10), padx=10, fill="x")

        answer4 = ctk.CTkEntry(master=frame, placeholder_text="Answer 4", height=32)
        answer4.pack(pady=(0, 10), padx=10, fill="x")

        checks_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        checks_row.pack(pady=(4, 10), padx=0, anchor="w")

        label4 = ctk.CTkLabel(master=checks_row, text="Correct Answer")
        label4.pack(side="left", padx=(10, 20))

        cb1 = ctk.CTkCheckBox(master=checks_row, text="1", width=60, checkbox_width=24, checkbox_height=24)
        cb1.pack(side="left", padx=(0, 3))

        cb2 = ctk.CTkCheckBox(master=checks_row, text="2", width=60, checkbox_width=24, checkbox_height=24)
        cb2.pack(side="left", padx=(0, 3))

        cb3 = ctk.CTkCheckBox(master=checks_row, text="3", width=60, checkbox_width=24, checkbox_height=24)
        cb3.pack(side="left", padx=(0, 3))

        cb4 = ctk.CTkCheckBox(master=checks_row, text="4", width=60, checkbox_width=24, checkbox_height=24)
        cb4.pack(side="left")

        def sendQuestion():
            """Send the question and answers to all connected clients"""
            question = entry1.get().strip()
            a1 = answer1.get().strip()
            a2 = answer2.get().strip()
            a3 = answer3.get().strip()
            a4 = answer4.get().strip()

            correct_answer = "0"
            if cb1.get():
                correct_answer = "1"
            elif cb2.get():
                correct_answer = "2"
            elif cb3.get():
                correct_answer = "3"
            elif cb4.get():
                correct_answer = "4"

            if not question:
                print("[ERROR] Question is empty")
                return

            # Set correct answer so recieve_answer can grade it
            with self.clients_lock:
                self.current_correct = correct_answer

            fields = [question, a1, a2, a3, a4, correct_answer]
            for client_sock in list(self.clients):
                try:
                    for field in fields:
                        payload = field.encode(self.FORMAT)
                        send_length = str(len(payload)).encode(self.FORMAT)
                        send_length += b' ' * (HEADER - len(send_length))
                        client_sock.send(send_length)
                        client_sock.send(payload)
                except Exception as e:
                    print(f"[WARN] Failed to send to client: {e}")
                    try:
                        self.clients.remove(client_sock)
                        client_sock.close()
                    except:
                        pass

        middle_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        middle_row.pack(pady=0, padx=0, fill="x")

        button_prev = ctk.CTkButton(master=middle_row, text="Previous")
        button_prev.pack(side="left", padx=10)

        button_next = ctk.CTkButton(master=middle_row, text="Next")
        button_next.pack(side="right", padx=10)

        bottom_row = ctk.CTkFrame(master=frame, fg_color="transparent")
        bottom_row.pack(pady=(10, 0), padx=0, fill="x")

        button3 = ctk.CTkButton(master=bottom_row, text="Send", height=32, command=sendQuestion)
        button3.pack(pady=10, padx=10)

        # --- LEADERBOARD TAB ---
        frame_leaderboard = ctk.CTkFrame(master=tab_Leaderbord)
        frame_leaderboard.pack(fill="both", expand=True)

        top_row_leaderboard = ctk.CTkFrame(master=frame_leaderboard, fg_color="transparent")
        top_row_leaderboard.pack(pady=(4, 10), padx=0, fill="x")

        label5 = ctk.CTkLabel(master=top_row_leaderboard, text="Leaderboard", font=("Roboto", 24))
        label5.pack(pady=12, padx=10, side="left")

        self.leaderboard_textbox = ctk.CTkTextbox(master=frame_leaderboard, height=300)
        self.leaderboard_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.leaderboard_textbox.configure(state="disabled")

        # --- QUESTIONS TAB ---
        frame_questions = ctk.CTkFrame(master=tab_questions)
        frame_questions.pack(fill="both", expand=True)

        top_row_questions = ctk.CTkFrame(master=frame_questions, fg_color="transparent")
        top_row_questions.pack(pady=(4, 10), padx=0, fill="x")

        label5 = ctk.CTkLabel(master=top_row_questions, text="Create Question", font=("Roboto", 24))
        label5.pack(pady=12, padx=10, side="left")

        label6 = ctk.CTkLabel(master=frame_questions, text="New Question")
        label6.pack(pady=(12, 2), padx=10, anchor="w")

        entry2 = ctk.CTkEntry(master=frame_questions, placeholder_text="Question", height=32)
        entry2.pack(pady=(0, 10), padx=10, fill="x")

        label3 = ctk.CTkLabel(master=frame_questions, text="Answers")
        label3.pack(pady=0, padx=10, anchor="w")

        answer1_questions = ctk.CTkEntry(master=frame_questions, placeholder_text="Answer 1", height=32)
        answer1_questions.pack(pady=(0, 10), padx=10, fill="x")

        answer2_questions = ctk.CTkEntry(master=frame_questions, placeholder_text="Answer 2", height=32)
        answer2_questions.pack(pady=(0, 10), padx=10, fill="x")

        answer3_questions = ctk.CTkEntry(master=frame_questions, placeholder_text="Answer 3", height=32)
        answer3_questions.pack(pady=(0, 10), padx=10, fill="x")

        answer4_questions = ctk.CTkEntry(master=frame_questions, placeholder_text="Answer 4", height=32)
        answer4_questions.pack(pady=(0, 10), padx=10, fill="x")

        checks_row_questions = ctk.CTkFrame(master=frame_questions, fg_color="transparent")
        checks_row_questions.pack(pady=(4, 10), padx=0, anchor="w")

        label6 = ctk.CTkLabel(master=checks_row_questions, text="Correct Answer")
        label6.pack(side="left", padx=(10, 20))

        cb1_questions = ctk.CTkCheckBox(master=checks_row_questions, text="1", width=60, checkbox_width=24, checkbox_height=24)
        cb1_questions.pack(side="left", padx=(0, 3))

        cb2_questions = ctk.CTkCheckBox(master=checks_row_questions, text="2", width=60, checkbox_width=24, checkbox_height=24)
        cb2_questions.pack(side="left", padx=(0, 3))

        cb3_questions = ctk.CTkCheckBox(master=checks_row_questions, text="3", width=60, checkbox_width=24, checkbox_height=24)
        cb3_questions.pack(side="left", padx=(0, 3))

        cb4_questions = ctk.CTkCheckBox(master=checks_row_questions, text="4", width=60, checkbox_width=24, checkbox_height=24)
        cb4_questions.pack(side="left")

        bottom_row_questions = ctk.CTkFrame(master=frame_questions, fg_color="transparent")
        bottom_row_questions.pack(pady=(4, 10), padx=0, fill="x")

        button3_questions = ctk.CTkButton(master=bottom_row_questions, text="Add Question", height=32)
        button3_questions.pack(pady=10, padx=10)

        # Start listening for answers from each client
        self.start_listening_for_answers()
        self.update_leaderboard_ui()

    def set_inittial_scores(self, scores):
        with self.clients_lock: 
            self.scores = dict(scores)
        self.update_leaderboard_ui()

    def add_clients(self,client_sock,addr):
        """Register a new client and start listening for their messages"""
        with self.clients_lock:
            if client_sock not in self.clients:
                self.clients.append(client_sock)
        self._start_listening_for_client(client_sock,addr)

    def _start_listening_for_client(self,client_sock, addr):
        with self.clients_lock:
            if client_sock in self.clients_listen:
                return
            self.clients_listen.add(client_sock)
        thread = threading.Thread(
            target=self.recieve_answer, args=(client_sock,addr),daemon=True
        )
        thread.start()

    def recieve_answer(self, client_sock, addr):
        """Listen for answers and names from a specific client"""
        try:
            while True:
                msg_length = client_sock.recv(self.HEADER).decode(self.FORMAT).strip()
                if not msg_length:
                    continue

                msg_length = int(msg_length)
                msg = client_sock.recv(msg_length).decode(self.FORMAT)

                if not msg:
                    continue

                # Extract name from join message
                if " has joined the server" in msg:
                    name = msg.split(" has joined the server")[0]
                    with self.clients_lock:
                        self.client_names[client_sock] = name
                        if name not in self.scores:
                            self.scores[name] = 0
                    print(f"[JOIN] {name}")
                    self.after(0,self.update_leaderboard_ui)

                elif ":" in msg:
                    name_part, score_part = msg.split(":",1)
                    name = name_part.strip()
                    score_txt = score_part.strip()
                    if name and score_txt.isdigit():
                        with self.clients_lock:
                            self.scores[name] = int(score_txt)
                        self.after(0, self.update_leaderboard_ui)

                # Grade answer
                elif msg.isdigit():
                    with self.clients_lock:
                        name = self.client_names.get(client_sock, str(addr))
                        correct = self.current_correct
                    
                    if correct and msg == correct:
                        with self.clients_lock:
                            self.scores[name] += 1
                        print(f"[CORRECT] {name} +1 (total: {self.scores[name]})")
                        self.after(0,self.update_leaderboard_ui)
                    else:
                        print(f"[WRONG] {name} answered {msg} (correct was {correct})")

        except Exception as e:
            print(f"[ERROR] recieve_answer: {e}")
        finally:
            with self.clients_lock:
                if client_sock in self.client_names:
                    del self.client_names[client_sock]
                if client_sock in self.clients_listen.remove(client_sock):
                    self.clients_listen.remove(client_sock)
            try:
                client_sock.close()
            except:
                pass

    def send_leaderboard():
        

    def start_listening_for_answers(self):
        """Start a thread for each connected client to listen for answers"""
        for client_sock in list(self.clients):
            self._start_listening_for_client(client_sock, "unknown")

    def update_leaderboard_ui(self):
        with self.clients_lock:
            items = sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
            print(items)
        self.leaderboard_textbox.configure(state="normal")
        self.leaderboard_textbox.delete("1.0","end")
        if not items:
            self.leaderboard_textbox.insert("end", "No players yet.\n")
        else:
            for i, (name, score) in enumerate(items, start=1):
                self.leaderboard_textbox.insert("end", f"{i}. {name} - {score}\n")
        self.leaderboard_textbox.configure(state="disabled")

    def go_back(self):
        self.destroy()
        self.parent.deiconify()