import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover (With Audio)")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি অটোমেটিক ক্রপ, ফিল্টার এবং অডিওসহ সাইজ ছোট করে সরাসরি গ্যালারিতে ডাউনলোডের অপশন দেবে।")

uploaded_file = st.file_uploader("গ্যালারি থেকে ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "copyright_free_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ ভিডিও আপলোড সফল হয়েছে!")
    
    if st.button("🚀 Remove Copyright & Keep Audio"):
        with st.spinner("মিউজিকসহ ব্যাকগ্রাউন্ডে প্রসেসিং চলছে... একটু অপেক্ষা করুন"):
            try:
                # পুরোনো ফাইল থাকলে ডিলিট করা
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                # FFmpeg কমান্ড: চারপাশ থেকে ক্রপ, ব্রাইটনেস ফিল্টার এবং অডিওর স্পিড/পিচ ১.০৩ গুণ করা
                # একই সাথে বিটরেট কমিয়ে এমবি সাইজ ছোট করা
                command = [
                    'ffmpeg', '-i', input_path,
                    '-vf', 'crop=in_w-30:in_h-30:15:15,eq=brightness=0.04',
                    '-filter_complex', '[0:a]atempo=1.03[a]',
                    '-map', '0:v', '-map', '[a]',
                    '-c:v', 'libx264', '-b:v', '1200k',
                    '-c:a', 'aac', '-preset', 'veryfast', output_path
                ]
                
                # কমান্ড রান করা
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("🎉 আপনার ভিডিওর মিউজিকসহ কপিরাইট সফলভাবে রিমুভ করা হয়েছে!")
                    
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download)",
                            data=file,
                            file_name="copyright_free_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"প্রসেসিং ব্যর্থ হয়েছে। সার্ভার এরর: {result.stderr}")
                    
                # টেম্পোরারি ফাইল রিমুভ করা
                if os.path.exists(input_path): os.remove(input_path)
                
            except Exception as e:
                st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")