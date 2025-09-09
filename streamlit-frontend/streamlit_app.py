import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
import time
import os

# Page config
st.set_page_config(page_title="Image Generator", page_icon="🎨", layout="wide")

# Initialize session state for storing generated image
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "generation_info" not in st.session_state:
    st.session_state.generation_info = None
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = "A beautiful landscape with mountains and lakes"
if "generating" not in st.session_state:
    st.session_state.generating = False

# Title and description
st.title("🎨 Image Generator")
st.markdown(
    "Generate high-quality images with complex text rendering using Qwen-Image model"
)

# Sidebar for parameters
st.sidebar.header("Generation Parameters")

# API endpoint configuration
default_api_url = os.getenv("API_URL", "http://localhost:8000")
api_url = st.sidebar.text_input("API Endpoint", value=default_api_url)

# Generation parameters
prompt = st.text_area(
    "Prompt",
    value=st.session_state.current_prompt,
    height=100,
    help="Describe the image you want to generate",
)

col1, col2 = st.columns(2)

# Initialize session state for synchronized values
if "num_steps_value" not in st.session_state:
    st.session_state.num_steps_value = 50
if "cfg_scale_value" not in st.session_state:
    st.session_state.cfg_scale_value = 4.0

with col1:
    # Inference Steps with synchronized input
    st.write("**Inference Steps**")
    col1a, col1b = st.columns([3, 1])
    with col1a:
        num_steps_slider = st.slider(
            "Inference Steps Slider",
            10,
            50,
            value=st.session_state.num_steps_value,
            help="More steps = higher quality, slower generation",
            key="steps_slider",
            label_visibility="collapsed",
        )
    with col1b:
        num_steps_input = st.number_input(
            "Inference Steps Input",
            min_value=10,
            max_value=50,
            value=st.session_state.num_steps_value,
            key="steps_input",
            label_visibility="collapsed",
        )

    # Update session state based on which widget changed
    if num_steps_slider != st.session_state.num_steps_value:
        st.session_state.num_steps_value = num_steps_slider
        st.rerun()
    elif num_steps_input != st.session_state.num_steps_value:
        st.session_state.num_steps_value = num_steps_input
        st.rerun()
    num_steps = st.session_state.num_steps_value

with col2:
    # Aspect ratio selection
    aspect_ratios = {
        "Square (1:1)": (1328, 1328),
        "Landscape (16:9)": (1664, 928),
        "Portrait (9:16)": (928, 1664),
        "Photo (4:3)": (1472, 1140),
        "Portrait Photo (3:4)": (1140, 1472),
        "Wide (3:2)": (1584, 1056),
        "Tall (2:3)": (1056, 1584),
    }

    selected_ratio = st.selectbox("Aspect Ratio", list(aspect_ratios.keys()), index=0)
    width, height = aspect_ratios[selected_ratio]

    st.write(f"Resolution: {width} × {height}")

# Advanced Settings
st.markdown("---")
with st.expander("🔧 Advanced Settings"):
    col1, col2 = st.columns(2)

    with col1:
        # CFG Scale with synchronized input
        st.write("**CFG Scale**")
        cfg_col1, cfg_col2 = st.columns([3, 1])
        with cfg_col1:
            cfg_scale_slider = st.slider(
                "CFG Scale Slider",
                1.0,
                10.0,
                value=st.session_state.cfg_scale_value,
                step=0.5,
                help="Higher values follow prompt more closely",
                key="cfg_slider",
                label_visibility="collapsed",
            )
        with cfg_col2:
            cfg_scale_input = st.number_input(
                "CFG Scale Input",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.cfg_scale_value,
                step=0.5,
                key="cfg_input",
                label_visibility="collapsed",
            )

        # Update session state based on which widget changed
        if cfg_scale_slider != st.session_state.cfg_scale_value:
            st.session_state.cfg_scale_value = cfg_scale_slider
            st.rerun()
        elif cfg_scale_input != st.session_state.cfg_scale_value:
            st.session_state.cfg_scale_value = cfg_scale_input
            st.rerun()

        cfg_scale = st.session_state.cfg_scale_value

        # Negative prompt
        negative_prompt = st.text_area(
            "Negative Prompt",
            value="",
            height=80,
            help="Describe what you don't want in the image (leave empty for default)",
        )

        # Seed settings
        use_random_seed = st.checkbox("Use Random Seed", value=True)
        if use_random_seed:
            seed = -1  # Will be handled by backend
            st.info("🎲 Random seed will be used for each generation")
        else:
            seed = st.number_input(
                "Seed",
                min_value=0,
                max_value=2147483647,
                value=42,
                help="Set a specific seed for reproducible results",
            )

    with col2:
        # Positive magic suffix
        language = st.selectbox(
            "Language Enhancement",
            options=["English", "Chinese", "None"],
            index=0,
            help="Add quality enhancement suffix based on prompt language",
        )

        if language == "English":
            positive_magic = ", Ultra HD, 4K, cinematic composition."
        elif language == "Chinese":
            positive_magic = ", 超清，4K，电影级构图."
        else:
            positive_magic = ""

        if positive_magic:
            st.info(f"✨ Will add: '{positive_magic}'")

        # Custom positive magic
        custom_positive = st.text_input(
            "Custom Quality Enhancement",
            value="",
            help="Add your own quality enhancement text (will override language enhancement)",
        )

        if custom_positive:
            positive_magic = custom_positive

# Generate button
if st.button("🚀 Generate Image", type="primary"):
    if not prompt.strip():
        st.error("Please enter a prompt!")
    else:
        # Clear previous generation info when starting new generation
        st.session_state.generated_image = None
        st.session_state.generation_info = None
        st.session_state.generating = True

        # Prepare enhanced prompt
        enhanced_prompt = prompt
        if positive_magic:
            enhanced_prompt = prompt + positive_magic

        # Prepare payload
        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": negative_prompt if negative_prompt.strip() else " ",
            "num_inference_steps": num_steps,
            "width": width,
            "height": height,
            "true_cfg_scale": cfg_scale,
            "seed": seed,
        }

        # Show generation status
        with st.spinner("Generating image... This may take 30-60 seconds"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                start_time = time.time()

                # Make API request
                response = requests.post(
                    f"{api_url}/generate", json=payload, timeout=180
                )

                elapsed_time = time.time() - start_time

                if response.status_code == 200:
                    progress_bar.progress(100)
                    status_text.success(f"✅ Generated in {elapsed_time:.1f} seconds!")

                    # Decode and store image in session state
                    data = response.json()
                    img_data = base64.b64decode(data["image_base64"])
                    img = Image.open(BytesIO(img_data))

                    # Get the actual seed used (important for random seeds)
                    actual_seed = data.get("seed_used", seed)

                    # Store image and generation info in session state
                    st.session_state.generated_image = img
                    st.session_state.generation_info = {
                        "prompt": enhanced_prompt,
                        "original_prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "elapsed_time": elapsed_time,
                        "timestamp": int(time.time()),
                        "parameters": {
                            "steps": num_steps,
                            "cfg_scale": cfg_scale,
                            "resolution": f"{width}x{height}",
                            "seed": actual_seed,
                            "aspect_ratio": selected_ratio,
                            "language_enhancement": language,
                            "custom_enhancement": custom_positive,
                        },
                    }
                    st.session_state.generating = False

                else:
                    st.error(
                        f"Generation failed: {response.status_code} - {response.text}"
                    )

            except requests.exceptions.Timeout:
                st.error(
                    "⏰ Request timed out. The model might be loading or overloaded."
                )
                st.session_state.generating = False
            except requests.exceptions.ConnectionError:
                st.error(
                    f"❌ Cannot connect to API at {api_url}. Make sure the service is running."
                )
                st.session_state.generating = False
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.generating = False

# Display generated image if it exists in session state and not currently generating
if st.session_state.generated_image is not None and not st.session_state.generating:
    st.markdown("---")
    st.subheader("Generated Image")

    # Display the image
    st.image(
        st.session_state.generated_image,
        caption=f"Generated: {st.session_state.generation_info['prompt'][:50]}...",
    )

    # Show generation details
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Generation Time",
            f"{st.session_state.generation_info['elapsed_time']:.1f}s",
        )
    with col2:
        st.metric("Steps", st.session_state.generation_info["parameters"]["steps"])
    with col3:
        st.metric(
            "Resolution", st.session_state.generation_info["parameters"]["resolution"]
        )
    with col4:
        st.metric("Seed", st.session_state.generation_info["parameters"]["seed"])

    # Show detailed parameters in expander
    with st.expander("📋 Generation Details"):
        st.write("**Original Prompt:**")
        st.code(st.session_state.generation_info["original_prompt"])

        if (
            st.session_state.generation_info["prompt"]
            != st.session_state.generation_info["original_prompt"]
        ):
            st.write("**Enhanced Prompt:**")
            st.code(st.session_state.generation_info["prompt"])

        if st.session_state.generation_info["negative_prompt"].strip():
            st.write("**Negative Prompt:**")
            st.code(st.session_state.generation_info["negative_prompt"])

        col1, col2 = st.columns(2)
        with col1:
            st.write(
                f"**CFG Scale:** {st.session_state.generation_info['parameters']['cfg_scale']}"
            )
            st.write(
                f"**Aspect Ratio:** {st.session_state.generation_info['parameters']['aspect_ratio']}"
            )
        with col2:
            st.write(
                f"**Inference Steps:** {st.session_state.generation_info['parameters']['steps']}"
            )
            st.write(
                f"**Seed:** {st.session_state.generation_info['parameters']['seed']}"
            )

    # Download button
    img_buffer = BytesIO()
    st.session_state.generated_image.save(img_buffer, format="PNG")
    st.download_button(
        label="📥 Download Image",
        data=img_buffer.getvalue(),
        file_name=f"qwen_image_{st.session_state.generation_info['timestamp']}.png",
        mime="image/png",
    )

    # Clear image button
    if st.button("🗑️ Clear Image"):
        st.session_state.generated_image = None
        st.session_state.generation_info = None
        st.rerun()

# Health check section
st.sidebar.markdown("---")
st.sidebar.subheader("Service Status")

if st.sidebar.button("Check Health"):
    try:
        health_response = requests.get(f"{api_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.sidebar.success("✅ Service is healthy")

            if "gpu_info" in health_data:
                gpu_info = health_data["gpu_info"]
                st.sidebar.write(f"GPUs: {gpu_info.get('gpu_count', 'N/A')}")
                if "gpu_memory" in gpu_info:
                    for i, mem in enumerate(gpu_info["gpu_memory"]):
                        st.sidebar.write(f"GPU {i}: {mem}")
        else:
            st.sidebar.error("❌ Service unhealthy")
    except:
        st.sidebar.error("❌ Cannot reach service")

# Example prompts
st.sidebar.markdown("---")
st.sidebar.subheader("Example Prompts")

example_prompts = [
    "A dynamic sports action shot of a skier launching off a massive jump, captured in a photorealistic style.",
    "Illustrate a poignant moment from a slice-of-life anime, with two high school friends sharing a heartfelt conversation under a cherry blossom tree, petals gently falling around them.",
    "Capture a heartwarming moment as a pair of emperor penguins tenderly care for their fluffy, gray chick amidst the harsh, icy landscape of Antarctica, with a soft, snowy backdrop.",
    "Insert a UFO landing in the background",
    "A beautiful Chinese young woman holding a marker with text 'AI' written on a whiteboard behind her",
    "A street scene with a shop sign displaying both English 'WELCOME' and Chinese '欢迎光临' in neon lights",
    "A book cover with the title 'AI Revolution' in elegant typography, with Chinese subtitle '人工智能革命'",
    "A vintage poster showing '1984' in bold letters with Chinese characters '一九八四' underneath",
    "A modern office building with a large LED display showing 'INNOVATION 创新' in glowing letters",
    "A traditional Chinese restaurant with a wooden sign reading '老北京饭店 Beijing Restaurant' in calligraphy",
]

for example in example_prompts:
    if st.sidebar.button(f"📝 {example[:30]}...", key=example):
        st.session_state.current_prompt = example
        st.rerun()
