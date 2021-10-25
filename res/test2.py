import matplotlib.pylab as l,scipy.ndimage as i
r=round
w=l.zeros((40,40),int)-1
p=l.matshow(w,vmax=2)
c=p.figure.canvas
def h(e):
 try:w[r(e.ydata),r(e.xdata)]=[0,2,-1][e.button-1]
 except:x=i.convolve(w==2,l.ones((3,3)),int,'constant');w[:]=w/2+((w==0)&(x>0)&(x<3))*2
 p.set_data(w);c.draw()
c.mpl_connect('button_press_event',h)
l.show()