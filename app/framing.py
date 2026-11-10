
import subprocess,shutil
from pathlib import Path
def render_face_tracked(source,output,start,duration,width=1080,height=1920):
    try: import cv2
    except ImportError as e: raise RuntimeError("OpenCV eksik: pip install opencv-python-headless") from e
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened(): raise RuntimeError("Video açılamadı.")
    fps=cap.get(cv2.CAP_PROP_FPS) or 25
    sw,sh=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not sw or not sh: cap.release(); raise RuntimeError("Çözünürlük okunamadı.")
    ratio=width/height
    cw,ch=(int(sh*ratio),sh) if sw/sh>ratio else (sw,int(sw/ratio))
    detector=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    temp=Path(output).with_name(Path(output).stem+"_silent.mp4")
    writer=cv2.VideoWriter(str(temp),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    cap.set(cv2.CAP_PROP_POS_MSEC,start*1000); cx=sw/2
    for _ in range(max(1,int(duration*fps))):
        ok,frame=cap.read()
        if not ok: break
        faces=detector.detectMultiScale(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),1.12,5,minSize=(50,50))
        if len(faces):
            x,y,w,h=max(faces,key=lambda b:b[2]*b[3]); cx=.78*cx+.22*(x+w/2)
        left=max(0,min(sw-cw,int(cx-cw/2))); top=max(0,(sh-ch)//2)
        writer.write(cv2.resize(frame[top:top+ch,left:left+cw],(width,height)))
    cap.release(); writer.release()
    if not shutil.which("ffmpeg"): raise RuntimeError("FFmpeg bulunamadı.")
    cmd=["ffmpeg","-y","-i",str(temp),"-ss",str(start),"-i",str(source),"-t",str(duration),"-map","0:v:0","-map","1:a?","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(output)]
    p=subprocess.run(cmd,capture_output=True,text=True); temp.unlink(missing_ok=True)
    if p.returncode: raise RuntimeError(p.stderr[-1500:])
    return Path(output)
