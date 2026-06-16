import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
import json

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("ভিডিও আপলোড করুন, সেকেন্ড বসিয়ে কেটে নিন এবং নিখুঁত ওয়াটারমার্ক যুক্ত করুন।")

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
    st.markdown("### 📺 ভিডিও প্রিভিউ:")
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    
    # --- ভিডিওর আসল দৈর্ঘ্য বের করা ---
    video_duration = 26.0
    try:
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        ffprobe_exe = ffmpeg_exe.replace("ffmpeg", "ffprobe")
        
        cmd = [ffprobe_exe, "-v", "error", "-show_entries", "format=duration", "-of", "json", input_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = json.loads(result.stdout)
        video_duration = float(info["format"]["duration"])
    except:
        pass

    video_duration = round(video_duration, 1)

    st.markdown("---")
    st.markdown(f"### ✂️ ভিডিও কাটিং সিস্টেম (মোট দৈর্ঘ্য: `{video_duration}` সেকেন্ড)")
    
    col1, col2 = st.columns(2)
    with col1:
        total_start_seconds = st.number_input("⏱️ শুরুর সেকেন্ড (Start):", min_value=0.0, max_value=float(video_duration), value=0.0, step=0.5)
    with col2:
        total_end_seconds = st.number_input("⏱️ শেষের সেকেন্ড (End):", min_value=0.1, max_value=float(video_duration), value=float(video_duration), step=0.5)
    
    st.markdown("---")
    
    # --- ওয়াটারমার্ক সিস্টেম ---
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক বা লোগো সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "লোগোর ছবি আপলোড করে (Image/Logo Watermark)", "কোনো ওয়াটারমার্ক ছাড়া (None)"])
    
    # বেসিক ক্রপ ও কালার ফিল্টার (কপিরাইট রিমুভার)
    base_vf = "crop=in_w-20:in_h-20:10:10,eq=brightness=0.03:contrast=1.03"
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
        
        # সুনির্দিষ্ট টেক্সট ফিল্টার যা ভিডিওর উপরে ডানপাশে বসবে
        if text_watermark:
            if text_style == "১. রেগুলার বোল্ড (Classic Bold)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:bold=1:box=1:boxcolor=black@0.4:boxborderw=4"
            elif text_style == "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=white:fontsize=28:italic=1:bold=1"
            elif text_style == "৩. গথিক/মডার্ন টাইপ (Modern Monospace)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=lightgray:fontsize=26"
            elif text_style == "৪. গোল্ডেন শ্যাডো বক্স (Golden Elegant Box)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=yellow:fontsize=26:bold=1:box=1:boxcolor=black@0.5:boxborderw=5"
            elif text_style == "৫. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=40:fontcolor=cyan:fontsize=28:bold=1:box=1:boxcolor=black@0.3"
            
            # বেস ফিল্টারের সাথে টেক্সট ফিল্টার জোড়া দেওয়া
            vf_final = f"{base_vf},{text_filter}"
            
    elif watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
        logo_file = st.file_uploader("আপনার লোগোর ছবি আপলোড করুন (PNG)", type=["png", "jpg", "jpeg"])
        if logo_file is not None:
            logo_uploaded = True
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
            # লোগো ওভারলে করার জন্য ক্যারেক্টার ফিল্টার চেইন
            vf_final = f"[0:v]{base_vf}[bg];movie=temp_logo.png,scale=60:60[logo];[bg][logo]overlay=main_w-overlay_w-40:40"
    else:
        vf_final = base_vf

    st.markdown("---")
    
    if st.button("🚀 Process, Cut & Remove Copyright"):
        if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)" and not logo_uploaded:
            st.error("❌ দয়া করে আপনার লোগোর ছবিটি আপলোড করুন!")
        elif total_start_seconds >= total_end_seconds:
            st.error("❌ ভুল সিলেকশন! ভিডিওর শেষের সময় অবশ্যই শুরুর সময়ের চেয়ে বেশি হতে হবে।")
        else:
            with st.spinner("ভিডিও প্রসেস ও ওয়াটারমার্ক যুক্ত করার কাজ চলছে..."):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    command = [
                        ffmpeg_exe, '-y',
                        '-ss', f"{total_start_seconds:.1f}",
                        '-to', f"{total_end_seconds:.1f}",
                        '-i', input_path
                    ]
                    
                    audio_filter = "asetrate=44100*1.04,atempo=1.02"
                    
                    # লোগো এবং টেক্সটের জন্য আলাদা আলাদা ১০০% কার্যকরী ফিল্টার কমপ্লেক্স লজিক
                    if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)":
                        command += [
                            '-filter_complex', f"{vf_final}[v_out];[0:a]{audio_filter}[a_out]",
                            '-map', '[v_out]', '-map', '[a_out]'
                        ]
                    else:
                        command += [
                            '-filter_complex', f"[0:v]{vf_final}[v_out];[0:a]{audio_filter}[a_out]",
                            '-map', '[v_out]', '-map', '[a_out]'
                        ]
                        
                    command += [
                        '-c:v', 'libx264', '-b:v', '1200k',
                        '-c:a', 'aac', '-b:a', '128k',
                        '-preset', 'veryfast', output_path
                    ]
                    
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 আলহামদুলিল্লাহ! ওয়াটারমার্কসহ ভিডিও সফলভাবে তৈরি হয়েছে।")
                        
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
