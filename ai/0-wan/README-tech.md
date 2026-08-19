# Telegram bot configuration

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_ALLOWED_CHAT_IDS="<chat-id>,<chat-id>"
```

PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

podman run --rm -it --device nvidia.com/gpu=all --shm-size=16g -v /ssd/internet:/ssd/internet:ro -v /ssd/home/Videos:/data wan bash

while true; do
  python3 generate.py --task t2v-A14B --size 1280*720 --ckpt_dir /ssd/internet/huggingface.co/Wan-AI/Wan2.2-T2V-A14B/ --offload_model False --convert_model_dtype --prompt "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage."
done

root@9729cbd30e67:~/Wan2.2# python3 generate.py --help
usage: generate.py [-h] [--task {t2v-A14B,i2v-A14B,ti2v-5B,animate-14B,s2v-14B}] [--size {720*1280,1280*720,480*832,832*480,704*1280,1280*704,1024*704,704*1024}] [--frame_num FRAME_NUM]
                   [--ckpt_dir CKPT_DIR] [--offload_model OFFLOAD_MODEL] [--ulysses_size ULYSSES_SIZE] [--t5_fsdp] [--t5_cpu] [--dit_fsdp] [--save_file SAVE_FILE] [--prompt PROMPT] [--use_prompt_extend]
                   [--prompt_extend_method {dashscope,local_qwen}] [--prompt_extend_model PROMPT_EXTEND_MODEL] [--prompt_extend_target_lang {zh,en}] [--base_seed BASE_SEED] [--image IMAGE]
                   [--sample_solver {unipc,dpm++}] [--sample_steps SAMPLE_STEPS] [--sample_shift SAMPLE_SHIFT] [--sample_guide_scale SAMPLE_GUIDE_SCALE] [--convert_model_dtype]
                   [--src_root_path SRC_ROOT_PATH] [--refert_num REFERT_NUM] [--replace_flag] [--use_relighting_lora] [--num_clip NUM_CLIP] [--audio AUDIO] [--enable_tts]
                   [--tts_prompt_audio TTS_PROMPT_AUDIO] [--tts_prompt_text TTS_PROMPT_TEXT] [--tts_text TTS_TEXT] [--pose_video POSE_VIDEO] [--start_from_ref] [--infer_frames INFER_FRAMES]

Generate a image or video from a text prompt or image using Wan

options:
  -h, --help            show this help message and exit
  --task {t2v-A14B,i2v-A14B,ti2v-5B,animate-14B,s2v-14B}
                        The task to run.
  --size {720*1280,1280*720,480*832,832*480,704*1280,1280*704,1024*704,704*1024}
                        The area (width*height) of the generated video. For the I2V task, the aspect ratio of the output video will follow that of the input image.
  --frame_num FRAME_NUM
                        How many frames of video are generated. The number should be 4n+1
  --ckpt_dir CKPT_DIR   The path to the checkpoint directory.
  --offload_model OFFLOAD_MODEL
                        Whether to offload the model to CPU after each model forward, reducing GPU memory usage.
  --ulysses_size ULYSSES_SIZE
                        The size of the ulysses parallelism in DiT.
  --t5_fsdp             Whether to use FSDP for T5.
  --t5_cpu              Whether to place T5 model on CPU.
  --dit_fsdp            Whether to use FSDP for DiT.
  --save_file SAVE_FILE
                        The file to save the generated video to.
  --prompt PROMPT       The prompt to generate the video from.
  --use_prompt_extend   Whether to use prompt extend.
  --prompt_extend_method {dashscope,local_qwen}
                        The prompt extend method to use.
  --prompt_extend_model PROMPT_EXTEND_MODEL
                        The prompt extend model to use.
  --prompt_extend_target_lang {zh,en}
                        The target language of prompt extend.
  --base_seed BASE_SEED
                        The seed to use for generating the video.
  --image IMAGE         The image to generate the video from.
  --sample_solver {unipc,dpm++}
                        The solver used to sample.
  --sample_steps SAMPLE_STEPS
                        The sampling steps.
  --sample_shift SAMPLE_SHIFT
                        Sampling shift factor for flow matching schedulers.
  --sample_guide_scale SAMPLE_GUIDE_SCALE
                        Classifier free guidance scale.
  --convert_model_dtype
                        Whether to convert model paramerters dtype.
  --src_root_path SRC_ROOT_PATH
                        The file of the process output path. Default None.
  --refert_num REFERT_NUM
                        How many frames used for temporal guidance. Recommended to be 1 or 5.
  --replace_flag        Whether to use replace.
  --use_relighting_lora
                        Whether to use relighting lora.
  --num_clip NUM_CLIP   Number of video clips to generate, the whole video will not exceed the length of audio.
  --audio AUDIO         Path to the audio file, e.g. wav, mp3
  --enable_tts          Use CosyVoice to synthesis audio
  --tts_prompt_audio TTS_PROMPT_AUDIO
                        Path to the tts prompt audio file, e.g. wav, mp3. Must be greater than 16khz, and between 5s to 15s.
  --tts_prompt_text TTS_PROMPT_TEXT
                        Content to the tts prompt audio. If provided, must exactly match tts_prompt_audio
  --tts_text TTS_TEXT   Text wish to synthesize
  --pose_video POSE_VIDEO
                        Provide Dw-pose sequence to do Pose Driven
  --start_from_ref      whether set the reference image as the starting point for generation
  --infer_frames INFER_FRAMES
                        Number of frames per clip, 48 or 80 or others (must be multiple of 4) for 14B s2v
