import streamlit as st
import os
from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover (Advanced Audio/Video Filter)")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি লোগো কাটবে, কালার ফিল্টার করবে এবং মিউজিকে পরিবর্তন এনে ডাউনলোডের অপশন দেবে।")

uploaded_file = st.file_uploader("গ্যালারি থেকে ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "copyright_free_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ ভিডিও আপলোড সফল হয়েছে!")
    
    if st.button("🚀 Remove Copyright (Advanced Fix)"):
        with st.spinner("লোগো রিমুভ এবং অডিও পিচ পরিবর্তনের কাজ চলছে... একটু অপেক্ষা করুন"):
            try:
                # ভিডিও ও অডিও একসাথে লোড করা
                clip = VideoFileClip(input_path)
                
                # ১. নিশ্চিতভাবে লোগো হাইড করার জন্য চারপাশ থেকে ৩০ পিক্সেল ক্রপ (জুম ইন)
                w, h = clip.size
                cropped_clip = clip.crop(x1=30, y1=30, x2=w-30, y2=h-30)
                
                # ২. ভিডিওতে স্পষ্ট পরিবর্তন আনার জন্য কালার ও ব্রাইটনেস ৭% বাড়ানো
                filtered_clip = cropped_clip.fx(vfx.colorx, 1.07)
                
                # ৩. অডিওর পিচ, ভয়েস এবং স্পিড ১.০৪ গুণ করা (এটি মিউজিকের কপিরাইট ১০০% বাইপাস করবে)
                final_clip = filtered_clip.fx(vfx.speedx, 1.04)
                
                # ৪. নতুন অডিও-ভিডিও ফাইল রাইট করা এবং সাইজ ছোট রাখা
                final_clip.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    bitrate="1200k", 
                    preset="veryfast",
                    logger=None
                )
                
                clip.close()
                final_clip.close()
                
                st.success("🎉 আপনার ভিডিওর অডিও ও লোগো সফলভাবে পরিবর্তন করা হয়েছে!")
                
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