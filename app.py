import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover")
st.write("ভিডিও আপলোড করুন। আপনার ভিডিও যতটুকু লম্বা, স্লাইডার ঠিক ততটুকুই দেখাবে।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    # --- ভিডিও প্লেয়ার ---
    st.markdown("### 📺 ভিডিও প্রিভিউ:")
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    
    # --- মুভিপাই (MoviePy) দিয়ে ভিডিওর আসল দৈর্ঘ্য বের করা ---
    video_duration = 26.0  # ডিফল্ট ব্যাকআপ
    try:
        clip = VideoFileClip(input_path)
        video_duration = clip.duration
        clip.close()  # ফাইলটি মেমোরি থেকে রিলিজ করা
    except Exception as e:
        st.warning(f"ভিডিওর দৈর্ঘ্য মাপতে সামান্য সমস্যা হয়েছে, ডিফল্ট সময় ব্যবহার করা হচ্ছে।")

    # সেকেন্ডকে সুন্দর করে রাউন্ড করা
    video_duration = round(video_duration, 2)

    st.markdown("---")
    st.markdown(f"### ✂️ ভিডিও কাটিং টাইমলাইন (ভিডিওর আসল সাইজ: `{video_duration}` সেকেন্ড)")
    
    # আপনার রিকোয়েস্ট অনুযায়ী: ভিডিও যতটুকু লম্বা, স্লাইডার ঠিক ততটুকুই রেঞ্জ নিবে
    time_range = st.slider(
        "🎞️ ভিডিওর কাটিং পয়েন্ট সিলেক্ট করুন (টেনে ছোট-বড় করুন):",
        min_value=0.0,
        max_value=float(video_duration),
        value=(0.0, float(video_duration)), # ডিফল্টভাবে পুরো ভিডিও সিলেক্ট থাকবে
        step=0.1,
        format="%.2f সেকেন্ড",
        help="বাম পাশের বাটনটি শুরুর সেকেন্ড এবং ডান পাশের বাটনটি শেষের সেকেন্ড।"
    )
    
    total_start_seconds = time_range[0]
    total_end_seconds = time_range[1]
    
    # সিলেক্ট করা সময়ের হিসাব দেখানো
    st.markdown(f"🎯 **আপনার সিলেক্ট করা সময়:** `{total_start_seconds:.2f}` সেকেন্ড থেকে `{total_end_seconds:.2f}` সেকেন্ড পর্যন্ত অংশ কাটা হবে। (মোট দৈর্ঘ্য হবে: `{round(total_end_seconds - total_start_seconds, 2)}` সেকেন্ড)")
    st.markdown("---")
    
    # --- ওয়াটারমার্ক সিস্টেম ---
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক বা লোগো সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "কোনো ওয়াটারমার্ক ছাড়া (None)"])
    
    # কপিরাইট রিমুভার ফিল্টার (সামান্য ক্রপ ও কালার অ্যাডজাস্টমেন্ট)
    base_vf = "crop=in_w-20:in_h-20:10:10,eq=brightness=0.03:contrast=1.03"
    
    if watermark_type == "পেজের নাম লিখে (Text Watermark)":
        text_watermark = st.text_input("আপনার পেজ বা চ্যানেলের নাম লিখুন (ইংরেজিতে):", "The Unknown codex")
        text_style = st.selectbox(
            "টেক্সটের ডিজাইন বা স্টাইল সিলেক্ট করুন:",
            [
                "১. রেগুলার বোল্ড (Classic Bold)", 
                "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)", 
                "৩. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)"
            ]
        )
        
        if text_watermark:
            if text_style == "১. রেগুলার বোল্ড (Classic Bold)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=h-th-40:fontcolor=white:fontsize=24:bold=1:box=1:boxcolor=black@0.4"
            elif text_style == "২. স্টাইলিশ বেঁকা-তেরা (Stylish Italic)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=h-th-40:fontcolor=white:fontsize=24:italic=1:bold=1"
            elif text_style == "৩. সাইয়ান গ্লো এফেক্ট (Cyan Glow Style)":
                text_filter = f"drawtext=text='{text_watermark}':x=w-tw-40:y=h-th-40:fontcolor=cyan:fontsize=24:bold=1"
            
            vf_final = f"{base_vf},{text_filter}"
    else:
        vf_final = base_vf

    st.markdown("---")
    
    if st.button("🚀 Process, Cut & Remove Copyright"):
        if total_start_seconds >= total_end_seconds:
            st.error("❌ ভুল সিলেকশন! ভিডিওর শেষের সময় অবশ্যই শুরুর সময়ের চেয়ে বেশি হতে হবে।")
        else:
            with st.spinner("ভিডিও প্রসেস, কাটিং ও কপিরাইট রিমুভ করার কাজ চলছে..."):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    # সুনির্দিষ্ট সেকেন্ড ধরে কাটার নিখুঁত কমান্ড
                    command = [
                        ffmpeg_exe, '-y',
                        '-ss', f"{total_start_seconds:.2f}",
                        '-to', f"{total_end_seconds:.2f}",
                        '-i', input_path
                    ]
                    
                    audio_filter = "asetrate=44100*1.04,atempo=1.02"
                    
                    command += [
                        '-filter_complex', f"[0:v]{vf_final}[v_out];[0:a]{audio_filter}[a_out]",
                        '-map', '[v_out]', '-map', '[a_out]',
                        '-c:v', 'libx264', '-b:v', '1200k',
                        '-c:a', 'aac', '-b:a', '128k',
                        '-preset', 'veryfast', output_path
                    ]
                    
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 আলহামদুলিল্লাহ! আপনার সিলেক্ট করা সময় অনুযায়ী ভিডিও সফলভাবে তৈরি হয়েছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="cut_copyright_removed.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ প্রসেস করা যায়নি। সার্ভার এরর ডিটেইলস নিচে দেওয়া হলো:")
                        st.code(result.stderr)
                    
                    if os.path.exists(input_path): os.remove(input_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
