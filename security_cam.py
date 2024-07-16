import cv2
import winsound
import datetime

# Function to ask user for input and return True or False
def get_user_preference(prompt):
    response = input(prompt + ' (y/n): ').strip().lower()
    return response == 'y'

# Ask user if they want to record unusual activity
record_activity = get_user_preference("Do you want to record unusual activity?")

# Ask user if they want to maintain a security log
maintain_log = get_user_preference("Do you want to maintain a security log?")

# Initialize the camera
cam = cv2.VideoCapture(0)
#records the video in mp4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Set the duration for recording after motion is detected (in seconds)
recording_duration = 5
frames_per_second = 20
recording_frames = recording_duration * frames_per_second

# Open log file if the user wants to maintain a log
log_file = open('security_log.txt', 'a') if maintain_log else None

out = None
recording = False
frame_count = 0
count = 0

while cam.isOpened():
    ret, frame1 = cam.read()
    ret, frame2 = cam.read()

    if not ret:
        break

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False

    for c in contours:
        if cv2.contourArea(c) < 5000:
            continue
        #motion is detected if its greater than 5000
        motion_detected = True
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #play sound 
        if motion_detected:
            winsound.PlaySound('super_sus.wav', winsound.SND_ASYNC)
            #windows default alert sound
            # winsound.PlaySound('default.mp3', winsound.SND_ASYNC)
            
            if record_activity and not recording:
                recording = True
                frame_count = 0
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                count+=1
                video_path = f'sus{count}_{timestamp}.mp4'
                out = cv2.VideoWriter(video_path, fourcc, frames_per_second, (frame1.shape[1], frame1.shape[0]))
                if maintain_log:
                    log_entry = f"Unusual behavior detected at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Video saved at {video_path}\n"
                    log_file.write(log_entry)

    if recording:
        out.write(frame1)
        frame_count += 1
        if frame_count >= recording_frames:
            recording = False
            out.release()

    cv2.imshow('Security Cam', frame1)

    if cv2.waitKey(10) == ord('q'):
        break

if recording:
    out.release()

cam.release()
cv2.destroyAllWindows()

if log_file:
    log_file.close()
