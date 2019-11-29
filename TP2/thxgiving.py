# happyTG.py
# Run this for a holiday message.
# Carpe diem! (And carve turkeyem!)
# David

from tkinter import *
def happyTG():

  msg = """
   0OO ooO                                         0OOOO0o   0Ooo
    O   @                                          O  o  o  O    o
    O   0                                             O    o
    O   o   o@OO   O0OOoO  @OO0Oo  oo@ OOo            o    0
    Oo0OO       o   O    @  O    O  o   O             0    O
    o   O   @OOOX   X    X  X    X  X   X             X    X   XXX
    X   X  X    X   X    X  X    X   X X              X    X     X
    X   X  X    X   X    X  X    X   X X              X     X    X
   XXX XXX  XXXX X  XXXXX   XXXXX     X              XXX     XXXX
                    X       X         X
                   XXX     XXX      XX
  """

  def f(t):
      s = ""
      for c in t:
          if (not c.isspace() and (c != "X")): s += c
      (r,c,a,t) = ([],0,1,[72])
      for d in (reversed(s)):
          if (d.isalpha()): (c,a) = (c+d.isupper()*a, a+a)
          else:
              r+=[(1-ord(d)//50*2)*c]
              (c,a) = (0,1)
      for v in r[::-1]: t += [t[-1]+v]
      return "".join(map(chr,t)).replace("T"," T")+"!!!"
  s = f(msg)

  def tf():
      canvas.delete(ALL)
      for dx in [5,35]:
          f,x[0] = "Arial %d bold"%((x[0]+dx)%60),x[0]+dx//8
          canvas.create_text(300,150,text=s,fill="orange",font=f)
      canvas.after(250, tf)
  root,x = Tk(),[0]
  canvas = Canvas(root, width=600, height=300)
  canvas.pack()
  tf()
  root.mainloop()

happyTG()
