import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover (Termux Style)")
st.write("গ্যালারি থেকে ভিডিও আপলোড করুন। এটি অটোমেটিক লোগো কাটবে, কালার ফিল্টার করবে এবং মিউজিকের পিচ পরিবর্তন করে ডাউনলোডের অপশন দেবে।")

uploaded_file = st.file_uploader("গ্যালারি থেকে ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "copyright_free_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ ভিডিও আপলোড সফল হয়েছে!")
    
    if st.button("🚀 Remove Copyright (With Audio Fix)"):
        with st.spinner("টারমাক্স ইঞ্জিনে ব্যাকগ্রাউন্ডে প্রসেসিং চলছে... একটু অপেক্ষা করুন"):
            try:
                # পুরোনো কোনো ফাইল থাকলে তা ডিলিট করা
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                # টারমাক্সের সেই আসল FFmpeg কমান্ড যা অনলাইনে রান হবে:
                # ১. চারপাশ থেকে ৩০ পিক্সেল ক্রপ (লোগো ও ওয়াটারমার্ক সম্পূর্ণ গায়েব)
                # ২. কালার ও ব্রাইটনেস চেঞ্জ
                # ৩. অডিওর পিচ ও স্পিড পরিবর্তন (মিউজিক কপিরাইট বাইপাস)
                command = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-vf', 'crop=in_w-60:in_h-60:30:30,eq=brightness=0.06:contrast=1.05',
                    '-filter_complex', '[0:a]asetrate=44100*1.04,atempo=1.02[a]',
                    '-map', '0:v', '-map', '[a]',
                    '-c:v', 'libx264', '-b:v', '1200k',
                    '-c:a', 'aac', '-preset', 'veryfast', output_path
                ]
                
                # কমান্ডটি ব্যাকগ্রাউন্ডে রান করা
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("🎉 আপনার ভিডিওর মিউজিক ও লোগো সফলভাবে পরিবর্তন করা হয়েছে!")
                    
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download)",
                            data=file,
                            file_name="copyright_free_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"প্রসেস করা সম্ভব হয়নি। সার্ভার এরর: {result.stderr}")
                    
                # কাজ শেষে টেম্পোরারি ফাইল ডিলিট
                if os.path.exists(input_path): os.remove(input_path)
                
            except Exception as e:
                st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")