import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover (Universal Fix)")
st.write("আপনার ভিডিওটি আপলোড করুন। চারপাশের লোগো কাটার পাশাপাশি স্ক্রিনের যেকোনো জায়গার ওয়াটারমার্ক ঝাপসা করার সুবিধা নিচে দেওয়া হলো।")

uploaded_file = st.file_uploader("গ্যালারি থেকে ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "copyright_free_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ ভিডিও আপলোড সফল হয়েছে!")
    
    st.markdown("---")
    st.markdown("### 🎯 ওয়াটারমার্ক/লোগো রিমুভ করার অপশন:")
    
    # অপশন সিলেক্ট করা
    mode = st.radio(
        "কীভাবে ওয়াটারমার্ক লুকাতে চান?",
        ["১. চারপাশ ক্রপ করে লোগো বাদ দিন (সবচেয়ে সহজ ও অটোমেটিক)", "২. স্ক্রিনের নির্দিষ্ট জায়গায় ব্লার/ঝাপসা বক্স বসান (কাস্টম)"]
    )
    
    # ডিফল্ট ফিল্টার (ক্রপ ও ব্রাইটনেস)
    vf_filters = "crop=in_w-60:in_h-60:30:30,eq=brightness=0.06:contrast=1.05"
    
    if "২. স্ক্রিনের নির্দিষ্ট জায়গায়" in mode:
        st.info("💡 ভিডিওর লোগোটি স্ক্রিনের আনুমানিক কোন পজিশনে আছে তা নিচের স্লাইডার দিয়ে ঠিক করুন।")
        
        # বাম থেকে ডানের দূরত্ব (X) এবং উপর থেকে নিচের দূরত্ব (Y)
        blur_x = st.slider("বাম থেকে ডানের পজিশন (Horizontal)", 0, 100, 50, help="লোগোটি ডানে থাকলে মান বাড়ান, বামে থাকলে কমান।")
        blur_y = st.slider("উপর থেকে নিচের পজিশন (Vertical)", 0, 100, 20, help="লোগোটি নিচে থাকলে মান বাড়ান, ওপরে থাকলে কমান।")
        
        # পার্সেন্টেজ হিসাব করে FFmpeg ফিল্টারে বসানো
        vf_filters += f",delogo=x=(main_w-160)*{blur_x}/100:y=(main_h-60)*{blur_y}/100:w=160:h=60"
    
    st.markdown("---")
    
    if st.button("🚀 Remove Copyright & Process Video"):
        with st.spinner("ইঞ্জিনে ব্যাকগ্রাউন্ডে প্রсеসিং চলছে... একটু অপেক্ষা করুন"):
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                # ফাইনাল FFmpeg কমান্ড (মিউজিক পিচ ও স্পিড পরিবর্তনসহ)
                command = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-vf', vf_filters,
                    '-filter_complex', '[0:a]asetrate=44100*1.04,atempo=1.02[a]',
                    '-map', '0:v', '-map', '[a]',
                    '-c:v', 'libx264', '-b:v', '1200k',
                    '-c:a', 'aac', '-preset', 'veryfast', output_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    st.success("🎉 আপনার ভিডিওর মিউজিক, লোগো এবং ওয়াটারমার্ক সফলভাবে পরিবর্তন করা হয়েছে!")
                    
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download)",
                            data=file,
                            file_name="copyright_free_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"প্রসেস করা সম্ভব হয়নি। সার্ভার এরর: {result.stderr}")
                    
                if os.path.exists(input_path): os.remove(input_path)
                
            except Exception as e:
                st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")