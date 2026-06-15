import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video Copyright Remover", page_icon="🎬", layout="centered")

st.title("🎬 Smart Video Copyright Remover, Preview Cutter & Watermark Adder")
st.write("ভিডিও আপলোড করুন, প্লেয়ারে দেখে সময় নির্ধারণ করে কাটুন এবং আপনার নিজস্ব স্টাইলিশ ওয়াটারমার্ক বসান।")

uploaded_file = st.file_uploader("১. গ্যালারি থেকে মূল ভিডিও সিলেক্ট করুন (MP4)", type=["mp4"])

if uploaded_file is not None:
    input_path = "temp_input.mp4"
    output_path = "my_branded_video.mp4"
    logo_path = "temp_logo.png"
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
        
    st.success("✅ মূল ভিডিও আপলোড সফল হয়েছে!")
    st.markdown("---")
    
    # --- নতুন ফিচার: ভিডিও প্রিভিউ দেখে কাটার সিস্টেম ---
    st.markdown("### 📺 ভিডিওটি দেখে কাটার সময় (Seconds) নির্ধারণ করুন:")
    st.info("💡 নিচের ভিডিও প্লেয়ারটি চালু করুন এবং দেখে নিন কত সেকেন্ড থেকে কত সেকেন্ড পর্যন্ত আপনি রাখতে চান।")
    
    # স্ক্রিনে ভিডিও প্লেয়ার শো করা
    with open(input_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    
    # ইউজার ভিডিও দেখে এখানে সেকেন্ড বসাবেন
    col1, col2 = st.columns(2)
    with col1:
        trim_start = st.number_input("কত সেকেন্ড থেকে ভিডিও শুরু হবে? (Start Second)", min_value=0, value=0, step=1, help="ভিডিওর শুরুর যে অংশ বাদ দিতে চান, তার পরের সেকেন্ডটি এখানে লিখুন।")
    with col2:
        trim_end = st.number_input("কত সেকেন্ডে ভিডিও শেষ হবে? (End Second)", min_value=0, value=0, step=1, help="ভিডিওর যতটুকু রাখতে চান, প্লেয়ার দেখে সেই শেষ সেকেন্ডটি এখানে লিখুন। (পুরো ভিডিও রাখতে চাইলে ০ দিন)")
    
    st.markdown("---")
    
    # --- ফিচার ২: ওয়াটারমার্ক সিস্টেম ---
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
                    
                    # FFmpeg কমান্ড তৈরি করা
                    command = ['ffmpeg', '-y']
                    
                    # শুরুর সময় সেট করা (-ss)
                    if trim_start > 0:
                        command += ['-ss', str(trim_start)]
                    
                    # শেষের সময় সেট করা (-to)
                    if trim_end > 0:
                        command += ['-to', str(trim_end)]
                        
                    command += ['-i', input_path]
                    
                    # অডিও ও ভিডিও ফিল্টার সেটআপ
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
                    
                    # কমান্ড রান করা
                    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        st.success("🎉 চমৎকার! আপনার ভিডিওটি দেখে নিখুঁতভাবে কাটা ও তৈরি করা হয়েছে।")
                        
                        with open(output_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name="my_branded_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        if os.path.exists(output_path):
                            st.success("🎉 আপনার ভিডিওটি সফলভাবে রেডি হয়েছে!")
                            with open(output_path, "rb") as file:
                                st.download_button( label="⬇️ গ্যালারিতে সেভ করুন", data=file, file_name="processed_video.mp4", mime="video/mp4" )
                        else:
                            st.error(f"প্রসেস করা সম্ভব হয়নি। সার্ভার এরর।")
                    
                    if os.path.exists(input_path): os.remove(input_path)
                    if os.path.exists(logo_path): os.remove(logo_path)
                    
                except Exception as e:
                    st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
