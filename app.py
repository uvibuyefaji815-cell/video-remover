import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover & Watermark Adder")
st.write("আপনার ভিডিওটি আপলোড করুন। এটি কপিরাইট কাটবে এবং ভিডিওতে আপনার নিজস্ব স্টাইলিশ লোগো বা টেক্সট বসিয়ে দেবে।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    logo_path = "temp_logo.png"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "লোগোর ছবি আপলোড করে (Image/Logo Watermark)"])
    
    # বেসিক ফিল্টার (ক্রপ ও ব্রাইটনেস পরিবর্তন)
    vf_filters = "crop=in_w-40:in_h-40:20:20,eq=brightness=0.05:contrast=1.04"
    logo_uploaded = False
    
    if watermark_type == "পেজের নাম লিখে (Text Watermark)":
        text_watermark = st.text_input("আপনার পেজ বা চ্যানেলের নাম লিখুন (ইংরেজিতে):", "CineVideo BD")
        
        # ইংরেজি ফন্টের সুন্দর এবং চমৎকার ডিজাইনের অপশনগুলো
        text_style = st.selectbox(
            "টেক্সটের ডিজাইন বা স্টাইল সিলেক্ট করুন:",
            [
                "১. রেগুলার বোল্ড (Classic Bold)", 
                "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)", 
                "৩. গথিক/মডার্ন টাইপ (Modern Monospace)",
                "৪. গোল্ডেন শ্যাডো বক্স (Golden Elegant Box)",
                "৫. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)"
            ]
        )
        
        if text_watermark:
            # ডানপাশে উপরে কর্নারে সেট করার জন্য FFmpeg drawtext ফিল্টার
            # x=w-tw-40 মানে ডানপাশ থেকে ৪০ পিক্সেল বামে, y=40 মানে একদম উপর থেকে ৪০ পিক্সেল নিচে
            if text_style == "১. রেগুলার বোল্ড (Classic Bold)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:font='Sans':bold=1:box=1:boxcolor=black@0.4:boxborderw=4"
                
            elif text_style == "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)":
                # আপনার পছন্দের বেঁকা-তেরা কার্সিভ টাইপ লুক দেওয়ার জন্য Serif Italic ব্যবহার করা হয়েছে
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:font='Serif':italic=1:bold=1"
                
            elif text_style == "৩. গথিক/মডার্ন টাইপ (Modern Monospace)":
                # কম্পিউটার টাইপিং বা প্রফেশনাল মডার্ন লুকের জন্য
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=lightgray:fontsize=26:font='Monospace':bold=1"
                
            elif text_style == "৪. গোল্ডেন শ্যাডো বক্স (Golden Elegant Box)":
                # সোনালী বা হলুদ রঙের প্রিমিয়াম লুকের জন্য বক্সসহ
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=yellow:fontsize=24:font='Serif':bold=1:italic=1:box=1:boxcolor=black@0.5:boxborderw=6"
                
            elif text_style == "৫. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)":
                # চমৎকার নিয়ন বা সাইয়ান কালার যা ভিডিওতে খুব সুন্দর ফোটে
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=cyan:fontsize=26:font='Sans':bold=1:box=1:boxcolor=black@0.3:boxborderw=4"
            
    else:
        logo_file = st.file_uploader("আপনার লোগোর ছবি আপলোড করুন (PNG format হলে সবচেয়ে ভালো হয়)", type=["png", "jpg", "jpeg"])
        if logo_file is not None:
            logo_uploaded = True
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
            
            # লোগোটি ডানপাশের উপরে কর্নারে (Top Right) বসবে (main_w-overlay_w-40:40)
            # লোগোর সাইজ সুন্দর দেখানোর জন্য ৬০x৬০ পিক্সেল করা হয়েছে
            vf_filters += ",movie=temp_logo.png,scale=60:60[logo];[in][logo]overlay=main_w-overlay_w-40:40[out]"

    st.markdown("---")
    
    if st.button("🚀 Process & Add My Watermark"):
        if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)" and not logo_uploaded:
            st.error("❌ দয়া করে আপনার লোগোর ছবিটি আপলোড করুন!")
        else:
            with st.spinner("ডানপাশে উপরে স্টাইলিশ ওয়াটারমার্ক বসানো এবং প্রসেসিংয়ের কাজ চলছে... একটু অপেক্ষা করুন"):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    # FFmpeg ফাইনাল কমান্ড
                    if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
                        command = [
                            'ffmpeg', '-y', '-i', input_path,
                            '-filter_complex', f"[0:v]{vf_filters};[0:a]asetrate=44100*1.04,atempo=1.02[a]",
                            '-map', '[out]', '-map', '[a]',
                            '-c:v', 'libx264', '-b:v', '1200k',
                            '-c:a', 'aac', '-preset', 'veryfast', output_path
                        ]
                    else:
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
                        st.success("🎉 চমৎকার! ডানপাশে উপরে আপনার স্টাইলিশ ওয়াটারমার্কসহ ভিডিও তৈরি হয়ে গেছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="my_branded_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"প্রসেস করা সম্ভব হয়নি। সার্ভার এরর: {result.stderr}")
                        
                    if os.path.exists(input_path): os.remove(input_path)
                    if os.path.exists(logo_path): os.remove(logo_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
