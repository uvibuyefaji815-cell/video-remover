import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from datetime import time
import json

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("ভিডিও আপলোড করুন এবং প্লেয়ারের ঠিক নিচে মোবাইলের মতো টাইমলাইন টেনে কেটে নিন।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    logo_path = "temp_logo.png"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    # --- ভিডিও প্লেয়ার ---
    st.markdown("### 📺 ভিডিও প্রিভিউ ও টাইমলাইন সিলেক্টর:")
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    
    # --- ভিডিওর আসল সময় (Duration) অটোমেটিক বের করার লজিক ---
    video_duration = 30 # কোনো কারণে ফেইল করলে ডিফল্ট ৩০ সেকেন্ড থাকবে
    try:
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        ffprobe_exe = ffmpeg_exe.replace("ffmpeg", "ffprobe")
        
        # ভিডিওর মেটাডাটা থেকে সঠিক সেকেন্ড বের করা
        cmd = [ffprobe_exe, "-v", "error", "-show_entries", "format=duration", "-of", "json", input_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        video_duration = int(float(info["format"]["duration"]))
    except:
        pass

    # সেকেন্ডকে মিনিট ও সেকেন্ডে রূপান্তর (স্লাইডারের ম্যাক্সিমাম লিমিটের জন্য)
    max_min = video_duration // 60
    max_sec = video_duration % 60
    
    # --- অটো-ফিট মোবাইল ফ্রেন্ডলি স্লাইডার ---
    # ভিডিওর সাইজ অনুযায়ী স্লাইডার ছোট-বড় হবে, তাই সহজে টানা যাবে
    time_range = st.slider(
        "🎞️ ভিডিওর কাটিং পয়েন্ট সিলেক্ট করুন (টেনে ছোট-বড় করুন):",
        min_value=time(0, 0, 0),
        max_value=time(0, max_min, max_sec), 
        value=(time(0, 0, 0), time(0, max_min, max_sec)), # নিজে থেকেই পুরো ভিডিও সিলেক্ট হয়ে থাকবে
        format="mm:ss",
        help="বামের বাটন টেনে শুরুর সময় এবং ডানের বাটন টেনে শেষের সময় সেট করুন।"
    )
    
    start_time = time_range[0]
    end_time = time_range[1]
    
    # ব্যাকগ্রাউন্ডের জন্য সেকেন্ড হিসাব
    total_start_seconds = start_time.minute * 60 + start_time.second
    total_end_seconds = end_time.minute * 60 + end_time.second
    
    st.markdown("### 🎯 আপনার সিলেক্ট করা সময়:")
    st.info(f"🎬 ভিডিওটি **{start_time.minute:02d}:{start_time.second:02d}** থেকে শুরু হয়ে **{end_time.minute:02d}:{end_time.second:02d}** পর্যন্ত কেটে রাখা হবে।")
    st.markdown("---")
    
    # --- ওয়াটারমার্ক সিস্টেম ---
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক বা লোগো সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "লোগোর ছবি আপলোড করে (Image/Logo Watermark)", "কোনো ওয়াটারমার্ক ছাড়া (None)"])
    
    vf_filters = "crop=in_w-40:in_h-40:20:20,eq=brightness=0.05:contrast=1.04"
    logo_uploaded = False
    
    if watermark_type == "পেজের নাম লিখে (Text Watermark)":
        text_watermark = st.text_input("আপনার পেজ বা চ্যানেলের নাম লিখুন (ইংরেজিতে):", "CineVideo BD")
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
            if text_style == "১. রেগুলার বোল্ড (Classic Bold)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:font='Sans':bold=1:box=1:boxcolor=black@0.4:boxborderw=4"
            elif text_style == "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:font='Serif':italic=1:bold=1"
            elif text_style == "৩. গথিক/মডার্ন টাইপ (Modern Monospace)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=lightgray:fontsize=26:font='Monospace':bold=1"
            elif text_style == "৪. গোল্ডেন শ্যাডো বক্স (Golden Elegant Box)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=yellow:fontsize=24:font='Serif':bold=1:italic=1:box=1:boxcolor=black@0.5:boxborderw=6"
            elif text_style == "৫. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)":
                vf_filters += f",drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=cyan:fontsize=26:font='Sans':bold=1:box=1:boxcolor=black@0.3:boxborderw=4"
            
    elif watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
        logo_file = st.file_uploader("আপনার লোগোর ছবি আপলোড করুন (PNG)", type=["png", "jpg", "jpeg"])
        if logo_file is not None:
            logo_uploaded = True
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
            vf_filters += ",movie=temp_logo.png,scale=60:60[logo];[in][logo]overlay=main_w-overlay_w-40:40[out]"

    st.markdown("---")
    
    if st.button("🚀 Process, Cut & Remove Copyright"):
        if watermark_type == "ลোগোর ছবি আপলোড করে (Image/Logo Watermark)" and not logo_uploaded:
            st.error("❌ দয়া করে আপনার লোগোর ছবিটি আপলোড করুন!")
        elif total_start_seconds >= total_end_seconds:
            st.error("❌ ভুল সিলেকশন! ভিডিওর শেষের সময় অবশ্যই শুরুর সময়ের চেয়ে বেশি হতে হবে।")
        else:
            with st.spinner("ভিডিও প্রসেস ও কপিরাইট রিমুভের কাজ ব্যাকগ্রাউন্ডে চলছে..."):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    command = [
                        ffmpeg_exe, '-y',
                        '-ss', str(total_start_seconds),
                        '-to', str(total_end_seconds),
                        '-i', input_path
                    ]
                    
                    if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
                        command += [
                            '-filter_complex', f"[0:v]{vf_filters};[0:a]asetrate=44100*1.04,atempo=1.02[a]",
                            '-map', '[out]', '-map', '[a]'
                        ]
                    else:
                        command += [
                            '-vf', vf_filters,
                            '-filter_complex', '[0:a]asetrate=44100*1.04,atempo=1.02[a]',
                            '-map', '0:v', '-map', '[a]'
                        ]
                        
                    command += [
                        '-c:v', 'libx264', '-b:v', '1200k',
                        '-c:a', 'aac', '-preset', 'veryfast', output_path
                    ]
                    
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 আলহামদুলিল্লাহ! আপনার ভিডিওটি প্রপারলি এডিট করা হয়েছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="my_branded_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ প্রসেস করা যায়নি। সার্ভার এরর ডিটেইলস নিচে দেওয়া হলো:")
                        st.code(result.stderr)
                    
                    if os.path.exists(input_path): os.remove(input_path)
                    if os.path.exists(logo_path): os.remove(logo_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
