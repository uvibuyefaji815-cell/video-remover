import streamlit as st
import cv2
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি অটোমেটিক ক্রপ, ফিল্টার এবং সাইজ অপটিমাইজ করে সরাসরি গ্যালারিতে ডাউনলোডের অপশন দেবে।")

uploaded_file = st.file_uploader("গ্যালারি থেকে ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "copyright_free_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ ভিডিও আপলোড সফল হয়েছে!")
    
    if st.button("🚀 Remove Copyright & Optimize Size"):
        with st.spinner("ব্যাকগ্রাউন্ডে প্রসেসিং চলছে... একটু অপেক্ষা করুন"):
            try:
                # ভিডিও ওপেন করা
                cap = cv2.VideoCapture(input_path)
                
                # ভিডিওর সাইজ ও ফ্রেম রেট নেওয়া
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0 or fps is None: fps = 25.0
                
                # লোগো বা বর্ডার কাটার জন্য চারপাশ থেকে ১৫ পিক্সেল ক্রপ সাইজ হিসাব
                crop_x1, crop_y1 = 15, 15
                crop_x2, crop_y2 = width - 15, height - 15
                new_width = crop_x2 - crop_x1
                new_height = crop_y2 - crop_y1
                
                # ভিডিও রাইটার সেটআপ (এমবি সাইজ কমানোর জন্য mp4v কোডেক)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # ১. ক্রপ করা (লোগো রিমুভ)
                    cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                    
                    # ২. কালার ফিল্টার (ব্রাইটনেস সামান্য ৪% বাড়ানো যাতে কপিরাইট ডিটেক্ট না হয়)
                    filtered_frame = cv2.convertScaleAbs(cropped_frame, alpha=1.04, beta=2)
                    
                    # নতুন ফ্রেমে রাইট করা
                    out.write(filtered_frame)
                
                cap.release()
                out.release()
                
                st.success("🎉 আপনার ভিডিওর কপিরাইট সফলভাবে রিমুভ করা হয়েছে!")
                
                # সরাসরি ডাউনলোডের বাটন
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ গ্যালারিতে সেভ করুন (Download)",
                        data=file,
                        file_name="copyright_free_video.mp4",
                        mime="video/mp4"
                    )
                    
                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(output_path): os.remove(output_path)
                    
            except Exception as e:
                st.error(f"দুঃখিত, প্রসেস করার সময় একটি ইন্টারনাল এরর হয়েছে: {str(e)}")