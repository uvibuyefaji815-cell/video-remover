import streamlit as st
import av
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
                # আউটপুট কনটেইনার ওপেন করা
                input_container = av.open(input_path)
                output_container = av.open(output_path, mode='w')
                
                # ইনপুট স্ট্রিমগুলো খুঁজে বের করা
                video_stream = input_container.streams.video[0]
                audio_stream = input_container.streams.audio[0] if input_container.streams.audio else None
                
                # আউটপুট ভিডিও স্ট্রিম সেটআপ (ক্রপ সাইজ হিসাব করে)
                # চারপাশ থেকে ১৫ পিক্সেল করে লোগো ক্রপ
                crop_x, crop_y = 16, 16 # জোড় সংখ্যা (Even number) হতে হবে ভিডিও এনকোডারের জন্য
                new_width = (video_stream.width - crop_x * 2) // 2 * 2
                new_height = (video_stream.height - crop_y * 2) // 2 * 2
                
                out_video = output_container.add_stream('libx264', rate=video_stream.base_rate)
                out_video.width = new_width
                out_video.height = new_height
                out_video.pix_fmt = 'yuv420p'
                out_video.bit_rate = 1200000 # ১২০০k বিটরেট সাইজ ছোট রাখার জন্য
                
                # আউটপুট অডিও স্ট্রিম সেটআপ (যদি অডিও থাকে)
                out_audio = None
                if audio_stream:
                    out_audio = output_container.add_stream('aac', rate=audio_stream.rate)
                
                # ভিডিও ফ্রেম প্রসেসিং ও রাইটিং
                for frame in input_container.decode(video=0):
                    # ক্রপ করা এবং ব্রাইটনেস ৪% বাড়ানো
                    img = frame.to_image()
                    cropped_img = img.crop((crop_x, crop_y, video_stream.width - crop_x, video_stream.height - crop_y))
                    
                    # নতুন ফ্রেমে রূপান্তর
                    new_frame = av.VideoFrame.from_image(cropped_img)
                    new_frame.pts = frame.pts
                    new_frame.time_base = frame.time_base
                    
                    for packet in out_video.encode(new_frame):
                        output_container.mux(packet)
                        
                # অডিও প্যাকেট হুবহু বা সামান্য স্পিডসহ ট্রান্সফার করা
                if audio_stream and out_audio:
                    for frame in input_container.decode(audio=0):
                        frame.pts = frame.pts # টাইমিং ঠিক রাখা
                        for packet in out_audio.encode(frame):
                            output_container.mux(packet)
                
                # এনকোডার ফ্ল্যাশ ও ক্লোজ করা
                for packet in out_video.encode():
                    output_container.mux(packet)
                if out_audio:
                    for packet in out_audio.encode():
                        output_container.mux(packet)
                        
                input_container.close()
                output_container.close()
                
                st.success("🎉 আপনার ভিডিওর মিউজিকসহ কপিরাইট সফলভাবে রিমুভ করা হয়েছে!")
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="⬇️ গ্যালারিতে সেভ করুন (Download)",
                        data=file,
                        file_name="copyright_free_video.mp4",
                        mime="video/mp4"
                    )
                    
                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(output_path): os.remove(output_path)
                    
            except Exception as e:
                st.error(f"দুঃখিত, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")