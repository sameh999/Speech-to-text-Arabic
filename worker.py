# import threading
# import os

# from threading import Thread
# from time import sleep

# from sqlalchemy import null

# def createfile(path_to_file):
#     with open(path_to_file) as f:
#         contents = f.readlines()


# def transcript_task(path_to_file):
#     thread = Thread(target=read, args=(path_to_file ))
#     thread.daemon = True
#     thread.start()
#     #return jsonify({'thread_name': str(thread.name),'started': True})
#     return 
# def read(path_to_file):
#     with open(path_to_file) as f:
#         contents = f.readlines()
#     return contents
# def reed_trans(path= 'results.txt' ,time = 120 ):
    
#     for i in range(time):
#         results = read(path)
#         sleep(5)
#         if results != null :
#             break
#     return results
