import os
from socket import *
from time import sleep
from textrank import Textrank
from stt_api import transcribe_gcs
from upload_gcs import upload_blob

tmp_sound_name = './sound.mp3'
tmp_text_name = './result.txt'

def init(sock, host="localhost", port=19608):
    sock.bind((host, port))
    sock.listen(1)

def __clear():
    os.remove(tmp_sound_name)
    os.remove(tmp_text_name)

def __textrank(summary_len, conn):
    tmp_text = open(tmp_text_name, 'r').read()
    summary = Textrank(summary_len, tmp_text, conn).summarize()
    for i in range(len(summary)):
        conn.sendall(('\n' + str(i+1) + ') ' + summary[i]).encode())
        sleep(0.6)

def __upload_file(conn, bucket):
    bucket_name = bucket
    source_file_name = tmp_sound_name[2:]
    destination_blob_name = source_file_name
    upload_blob(bucket_name, source_file_name, destination_blob_name, conn)
    gcs_url = 'gs://' + bucket_name + '/' + source_file_name
    transcribe_gcs(gcs_url, tmp_text_name, conn)

def __read_msg(conn, msg):
    data = msg[7:]
    f = open(tmp_sound_name, 'wb')

    while(data.find('[End]'.encode()) == -1):
        f.write(data)
        data = conn.recv(1024)
    f.write(data[:data.find('[End]'.encode())])
    f.close()

    data = data[data.find('[End]'.encode())+5:]
    if(len(data) != 0):
        summary_len = int(data)
    else:
        summary_len = int(conn.recv(1024).decode())

    return summary_len

def __start(conn, bucket, msg):
    summary_len = __read_msg(conn, msg)
    __upload_file(conn, bucket)
    __textrank(summary_len, conn)
    __clear()

def __parse(conn, bucket):
    msg = conn.recv(1024)
    if(msg == '[quit]'.encode()):
        conn.sendall(msg)
        sleep(0.3)
        return
    elif(msg.find('[Start]'.encode()) == 0):
        __start(conn, bucket, msg)

def __accept(sock):
    conn, addr = sock.accept()
    conn.sendall('[Info] 서버와 연결됐습니다.'.encode())
    sleep(0.3)
    return conn, addr

def func(sock, bucket):
    while(True):
        conn, addr = __accept(sock)
        while(True):
            __parse(conn, bucket)
        conn.close()

if(__name__ == '__main__'):
    serv_sock = socket(AF_INET, SOCK_STREAM)
    init(serv_sock)
    func(serv_sock, "cn-stt-storage")
    serv_sock.close()
