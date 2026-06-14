import streamlit as st
import os
from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি অটোমেটিক ক্রপ, ফিল্টার, অডিও পিচ চেঞ্জ এবং সাইজ ছোট করে সরাসরি গ্যালারিতে ডাউনলোডের অপশন দেবে।")

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
                clip = VideoFileClip(input_path)
                
                # ১. চারপাশ থেকে ১৫ পিক্সেল ক্রপ (লোগো ও বর্ডার কাটার জন্য)
                w, h = clip.size
                cropped_clip = clip.crop(x1=15, y1=15, x2=w-15, y2=h-15)
                
                # ২. কালার ফিল্টার (ব্রাইটনেস ৪% বাড়ানো)
                filtered_clip = cropped_clip.fx(vfx.colorx, 1.04)
                
                # ৩. অডিও পিচ ও স্পিড সামান্য পরিবর্তন (১.০২ গুণ)
                final_clip = filtered_clip.fx(vfx.speedx, 1.02)
                
                # ৪. কোয়ালিটি ঠিক রেখে এমবি সাইজ কমানো
                final_clip.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac",
                    bitrate="1200k", 
                    preset="medium",
                    logger=None
                )
                
                clip.close()
                final_clip.close()
                
                st.success("🎉 আপনার ভিডিওর কপিরাইট সফলভাবে রিমুভ করা হয়েছে!")
                
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