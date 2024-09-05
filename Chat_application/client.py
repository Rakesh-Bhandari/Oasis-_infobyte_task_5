import socket
import threading
import customtkinter as ctk
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from datetime import datetime
from PIL import Image

# Function to load chat history from the server
def load_chat_history():
    try:
        client_socket.send("REQUEST_HISTORY".encode('utf-8'))
        history_data = client_socket.recv(4096).decode('utf-8')
        if history_data:
            history_lines = history_data.splitlines()
            for line in history_lines:
                if line.strip():
                    try:
                        sender, date, time, msg = line.split('|')
                        if sender.strip()==username:
                            align="e"
                        elif sender.strip()=="Server":
                            align="center"
                        else :
                            align="w"
                        display_message(msg.strip(), align, sender.strip(), time.strip(), date.strip())
                    except ValueError:
                        messagebox.showerror('Error',f"Invalid history format: {line}")
    except Exception as e:
        messagebox.showerror('Error',f"Failed to load chat history: {e}")

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            try:
                sender, msg = message.split(":", 1)
                timestamp = datetime.now().strftime('%I:%M %p')
                
                if sender.strip()==username:
                    align="e"
                elif sender.strip()=="Server":
                    align="center"
                else :
                    align="w"
                display_message(msg.strip(), align, sender.strip(), timestamp)
            except ValueError:
                messagebox.showerror('Error',f"Invalid message format: {message}")
        except Exception as e:
            messagebox.showerror('Error',f"An error occurred: {e}")
            break

# Global variable to keep track of the last displayed date
last_displayed_date = None

# Function to display messages with a timestamp and date
def display_message(msg, align, sender, timestamp, date=""):
    global last_displayed_date

    # If the date has changed, display a new date label
    if date and date != last_displayed_date:
        last_displayed_date = date
        date_frame = ctk.CTkFrame(chat_frame, fg_color="lightgray", corner_radius=20)
        date_label = ctk.CTkLabel(date_frame, text=date, font=("Calibri", 15, "bold"), text_color="black", fg_color=date_frame.cget("fg_color"))
        date_label.pack(side='top', anchor="center", pady=5, padx=10)
        date_frame.pack(fill=Y, pady=5, padx=10, anchor="center")

    msg_frame = ctk.CTkFrame(chat_frame, fg_color="#DCF8C6" if align == "e" else "#FFF", corner_radius=20)
    
    sender_label = ctk.CTkLabel(msg_frame, text=f"  {sender}  ", font=("Calibri", 14), fg_color=msg_frame.cget("fg_color"), text_color="Red" if align == "e" else "#00F")
    msg_label = ctk.CTkLabel(msg_frame, text=msg.strip(), fg_color=msg_frame.cget("fg_color"), font=("Calibri", 18), width=250, wraplength=250, anchor="w", corner_radius=20)
    time_label = ctk.CTkLabel(msg_frame, text=timestamp, font=("Calibri", 12), fg_color=msg_frame.cget("fg_color"), text_color="gray")

    sender_label.pack(side='top', anchor=align)
    msg_label.pack(side='top', fill="both", expand=True, padx=10, pady=5)
    time_label.pack(side='bottom', anchor='e', padx=10, pady=(0, 5))
    
    if align=="w":
        msg_frame.pack(fill=Y, pady=5, padx=10, anchor=align)
        
    elif align=="e":
        msg_frame.pack(fill=Y, pady=5, padx=75, anchor=align)
       
    else:
        msg_frame.pack(pady=5, padx=40,anchor='w')
        sender_label.configure(fg_color="gray",text_color="red",font=("Calibri", 18,'bold'))
        msg_frame.configure(fg_color="gray")
        msg_label.configure(fg_color="gray",anchor=align,font=("Calibri", 18,'italic'))
        time_label.destroy()

    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0) 
# Function to send messages to the server
def send_message():
    message = message_entry.get().strip()
    if message:
        try:
            client_socket.send(f"{username}:{message}".encode('utf-8'))
            message_entry.delete(0, 'end')
        except OSError as e:
            messagebox.showerror('Error',f"Failed to send message: {e}")

def exit_app():
    try:
        client_socket.close()
    except Exception as e:
        messagebox.showerror('Error',f"Error closing socket: {e}")
    app.destroy()
    exit(0)

# GUI setup
app = ctk.CTk()
app.geometry("360x640")  
app.title("Chat Application")
app.resizable(0, 0)  


header_frame = ctk.CTkFrame(app, height=40, width=360, fg_color="#075E54", corner_radius=0)
header_frame.place(x=0, y=0)

header = ctk.CTkLabel(header_frame, text="Live Chat Room", fg_color="#075E54", text_color="white", font=("Calibri", 14, "bold"), pady=10, height=40, anchor="w")
header.place(x=40, y=0)

exit_button = ctk.CTkButton(header_frame, text="⮌", command=exit_app, fg_color="#075E54", font=("Calibri", 24, 'bold'), height=40, width=40)
exit_button.place(x=0, y=0)

# Chat area
chat_canvas = Canvas(app, height=530, width=345)
chat_frame = ctk.CTkFrame(chat_canvas, fg_color="transparent")
scrollbar = ctk.CTkScrollbar(app, orientation="vertical", command=chat_canvas.yview, height=530, width=10)
chat_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.place(x=350, y=50)
chat_canvas.place(x=0, y=50)
chat_canvas.create_window((0, 0), window=chat_frame, anchor='nw')

chat_frame.bind("<Configure>", lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))

# Typing area using Entry widget and Send button
typing_frame = ctk.CTkFrame(app, fg_color="#d5e47e", height=60, width=360)
typing_frame.place(x=0, y=580)

message_entry = ctk.CTkEntry(typing_frame, font=("Calibri", 16), width=290, height=40, placeholder_text="Message", corner_radius=20, border_width=0)
message_entry.place(x=10, y=10)


send_img=ctk.CTkImage(light_image=Image.open('Chat_application/send.png'),size=(40,40))
send_button = ctk.CTkButton(typing_frame, text="",image=send_img, command=send_message,bg_color='#d5e47e', fg_color="#d5e47e", height=40, width=40,hover=0)
send_button.place(x=300, y=8)

# Prompt for username
username = simpledialog.askstring("Username", "Enter your username:")
if not username:
    messagebox.showerror('Invalid Username',"Username is required to connect.")
    app.destroy()
else:
    # Client setup
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 12345))  # Replace with the server's IP and port
        client_socket.send(username.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        if "invalid" in response:
            print(response)
            client_socket.close()
            app.destroy()
        else:
            # Load chat history from the server
            load_chat_history()

            # Start receiving messages in a new thread
            receive_messages_thread = threading.Thread(target=receive_messages, daemon=True)
            receive_messages_thread.start()

            app.mainloop()
    except ConnectionRefusedError:
        messagebox.showerror('Error',"Connection refused. Make sure the server is running and the IP/port are correct.")
        app.destroy()
