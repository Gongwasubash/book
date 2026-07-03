import subprocess, sys, time
p = subprocess.Popen([sys.executable, 'server.py'], cwd=r'E:\class  1 to 10 book\New folder\Nepal Textbooks Grade 1-10 - Markdown')
print(f"Server PID: {p.pid}")
# Write PID to file so we can kill later
with open('server.pid', 'w') as f:
    f.write(str(p.pid))
# Wait a bit for it to start
time.sleep(3)
# Check if still running
if p.poll() is None:
    print("Server started successfully")
else:
    print("Server failed to start")
