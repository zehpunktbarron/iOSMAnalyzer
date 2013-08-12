
for file in
with open("c0_create_hist_plp.py",'r+') as f:
  content = f.read()
  f.seek(0,0)
  line = "Das ist der Text der rein soll"
  f.write(line.rstrip('\r\n') + '\n' + content)
        
