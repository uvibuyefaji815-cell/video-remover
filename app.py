import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover (Mobile Slider Style)")
st.write("ভিডিও আপলোড করুন, মোবাইলের মতো টেনে টাইম সিলেক্ট করে কাটুন এবং নিজস্ব স্টাইলিশ ওয়াটারমার্ক বসান।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    logo_path = "temp_logo.png"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    # --- ভিডিও প্রিভিউ এবং মোবাইল স্টাইল স্লাইডার কাটিং ---
    st.markdown("### 📺 ভিডিওটি দেখে কাটার অংশ সিলেক্ট করুন:")
    st.info("💡 নিচের ভিডিও প্লেয়ারে দেখে নিন কত সেকেন্ড থেকে কত সেকেন্ড কাটবেন। তারপর স্লাইডারটি টেনে সেট করুন।")
    
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    
    # ভিডিওর আনুমানিক সর্বোচ্চ দৈর্ঘ্য (সেকেন্ডে) - ডিফল্ট ৩০০ সেকেন্ড বা ৫ মিনিট রাখা হয়েছে
    # এটি ইউজারকে মোবাইলের মতো দুই পাশ থেকে টেনে কাটার সুবিধা দেবে
    st.markdown("#### ⏳ ভিডিওর টাইমলাইন স্লাইডার (টেনে ছোট-বড় করুন):")
    time_range = st.slider(
        "ভিডিওর শুরুর এবং শেষের সেকেন্ড সিলেক্ট করুন:",
        min_value=0, 
        max_value=300, # সর্বোচ্চ ৩০০ সেকেন্ড (৫ মিনিট) পর্যন্ত স্লাইড করা যাবে 
        value=(0, 20), # ডিফল্টভাবে ০ থেকে ২০ সেকেন্ড সেট করা থাকবে
        step=1,
        help="বাম পাশের গোল বাটনটি টেনে শুরুর সময় এবং ডান পাশের বাটনটি টেনে শেষের সময় সেট করুন।"
    )
    
    total_start_seconds = time_range[0]
    total_end_seconds = time_range[1]
    
    st.write(f"🎯 **আপনার সিলেক্ট করা সময়:** {total_start_seconds} সেকেন্ড থেকে {total_end_seconds} সেকেন্ড পর্যন্ত কাটা হবে।")
    st.markdown("---")
    
    # --- ওয়াটারমার্ক সিস্টেম ---
    st.markdown("### 🎯 আপনার ওয়াটারমার্ক বা লোগো সেট করুন:")
    watermark_type = st.radio("কীভাবে ওয়াটারমার্ক লাগাতে চান?", ["পেজের নাম লিখে (Text Watermark)", "লোগোর ছবি আপলোড করে (Image/Logo Watermark)", "কোনো ওয়াটারমার্ক ছাড়া (None)"])
    
    # বেসিক কপিরাইট রিমুভাল ফিল্টার (ক্রপ ও ব্রাইটনেস)
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
        if watermark_type == "লোগোর ছবি আপলোড করে (Image/Logo Watermark)" and not logo_uploaded:
            st.error("❌ দয়া করে আপনার লোগোর ছবিটি আপলোড করুন!")
        else:
            with st.spinner("ভিডিও কাটিং এবং প্রসেসিংয়ের কাজ ব্যাকগ্রাউন্ডে চলছে... একটু অপেক্ষা করুন"):
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    
                    ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                    
                    # স্ট্যাবল কাটিং লজিক: ইনপুট ফাইলের আগেই -ss এবং -to ব্যবহার করে নিখুঁত ট্রিম
                    command = [ffmpeg_exe, '-y']
                    
                    if total_start_seconds > 0:
                        command += ['-ss', str(total_start_seconds)]
                    if total_end_seconds > 0:
                        command += ['-to', str(total_end_seconds)]
                        
                    command += ['-i', input_path]
                    
                    # ফিল্টার চেইন অ্যাড করা
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
                    
                    # সাবপ্রসেস রান করা
                    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    # এডিটেড ভিডিও আউটপুট চেক
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 চমৎকার! আপনার ভিডিওটি প্রপারলি এডিট করা হয়েছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="my_branded_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ প্রসেস করা যায়নি। দয়া করে কাটিংয়ের স্লাইডার বা টাইমলাইনটি আরেকবার চেক করুন।")
                    
                    # ক্লিনআপ ফাইল
                    if os.path.exists(input_path): os.remove(input_path)
                    if os.path.exists(logo_path): os.remove(logo_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
