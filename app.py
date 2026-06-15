import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover & Watermark Adder")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি কপিরাইট কাটবে এবং ভিডিওতে আপনার নিজস্ব লোগো বা নাম বসিয়ে দেবে।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    logo_path = "temp_logo.png"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    # ওয়াটারমার্কের ধরন সিলেক্ট করা
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "লোগোর ছবি আপলোড করে (Image/Logo Watermark)"])
    
    vf_filters = "crop=in_w-40:in_h-40:20:20,eq=brightness=0.05:contrast=1.04"
    logo_uploaded = False
    text_entered = False
    
    if watermark_type == "পেজের নাম লিখে (Text Watermark)":
        text_watermark = st.text_input("আপনার পেজ বা চ্যানেলের নাম লিখুন (ইংরেজিতে):", "CineVideo BD")
        if text_watermark:
            text_entered = True
            # ভিডিওর ডানদিকের নিচে নাম বসানোর ফিল্টার
            vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-20:y=h-th-20:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.4:boxborderw=5"
            
    else:
        logo_file = st.file_uploader("আপনার লোগোর ছবি আপলোড করুন (PNG format হলে সবচেয়ে ভালো হয়)", type=["png", "jpg", "jpeg"])
        if logo_file is not None:
            logo_uploaded = True
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
            # ভিডিওর ডানদিকের ওপরে লোগো বসানোর ফিল্টার (লোগো সাইট ৫০x৫০ সাইজে রিসাইজ হবে)
            vf_filters += ",movie=temp_logo.png,scale=50:50[logo];[in][logo]overlay=main_w-overlay_w-20:20[out]"

    st.markdown("---")
    
    if st.button("🚀 Process & Add My Watermark"):
        # যদি লোগো মোড সিলেক্ট থাকে কিন্তু লোগো আপলোড না করা হয়
        if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)" and not logo_uploaded:
            st.error("❌ দয়া করে আপনার লোগোর ছবিটি আপলোড করুন!")
        else:
            with st.spinner("আপনার ওয়াটারমার্ক বসানো এবং প্রসেসিংয়ের কাজ চলছে... একটু অপেক্ষা করুন"):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    # FFmpeg ফাইনাল কমান্ড (অডিও ও ভিডিও ফিল্টারসহ)
                    if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
                        # লোগো ওভারলে মোডের জন্য ম্যাপ ফিল্টার আলাদা হয়
                        command = [
                            'ffmpeg', '-y', '-i', input_path,
                            '-filter_complex', f"[0:v]{vf_filters};[0:a]asetrate=44100*1.04,atempo=1.02[a]",
                            '-map', '[out]', '-map', '[a]',
                            '-c:v', 'libx264', '-b:v', '1200k',
                            '-c:a', 'aac', '-preset', 'veryfast', output_path
                        ]
                    else:
                        # টেক্সট মোডের জন্য সাধারণ কমান্ড
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
                        st.success("🎉 চমৎকার! আপনার নিজস্ব ওয়াটারমার্কসহ ভিডিও তৈরি হয়ে গেছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="my_branded_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"প্রসেস করা সম্ভব হয়নি। সার্ভার এরর: {result.stderr}")
                        
                    # টেম্পোরারি ফাইল রিমুভ
                    if os.path.exists(input_path): os.remove(input_path)
                    if os.path.exists(logo_path): os.remove(logo_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
