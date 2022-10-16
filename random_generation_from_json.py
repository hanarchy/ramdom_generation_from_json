import math
import os
import sys
import traceback
import random
import json
import platform
import subprocess as sp
import copy
import re

import modules.scripts as scripts
import gradio as gr

from modules.processing import Processed, process_images
from PIL import Image
from modules.shared import opts, cmd_opts, state


def open_folder(f):
    if not os.path.isdir(f):
        print(f"""
WARNING
An open_folder request was made with an argument that is not a folder.
This could be an error or a malicious attempt to run code on your computer.
Requested path was: {f}
""", file=sys.stderr)
        return

    if not cmd_opts.hide_ui_dir_config:
        path = os.path.normpath(f)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            sp.Popen(["open", path])
        else:
            sp.Popen(["xdg-open", path])


def choice_value(data, key: str):
    return random.randint(data["min_" + key], data["max_" + key])


def choice_image_size(data, key: str):
    return random.choice(data[key])


class Script(scripts.Script):
    def title(self):
        return "Nandemo Unko"

    def ui(self, is_img2img):
        enable_check = gr.Checkbox(label="Enable", value=False)

        with gr.Row():
            directory = gr.Textbox(label="Prompts Directory",
                                   value="prompts", interactive=True)
            open_directory = gr.Button("Open Prompts Directory")
            open_directory.click(
                fn=open_folder,
                inputs=directory,
                outputs=[],
            )

        enable_check.change(fn=lambda x: [gr.TextArea.update(visible=x),
                                          gr.Button.update(visible=x)],
                            inputs=[enable_check],
                            outputs=[directory, open_directory])
        return [enable_check, directory, open_directory]

    def on_show(self, enable_check, directory, open_directory):
        return [gr.Checkbox.update(visible=True),
                gr.Textbox.update(visible=True),
                gr.Button.update(visible=True),
                ]

    def run(self, p, enable_check, directory, open_directory):
        from glob import glob
        if not enable_check:
            images = process_images(p).images
            return Processed(p, images, p.seed, "")

        p.do_not_save_grid = True

        files = glob(directory + "/*.json")

        jobs = []
        for fn in files:
            with open(fn) as f:
                data = json.load(f)
                job = dict()
                for k, v in data.items():
                    if re.match(r"^min_", k):
                        pass
                    elif re.match(r"^max_", k):
                        key = re.sub(r"max_", "", k)
                        val = choice_value(data, key)
                        job.update({key: val})
                    elif re.match(r"^image_sizes", k):
                        width, height = choice_image_size(data, k)
                        job.update({"width": width})
                        job.update({"height": height})

                    else:
                        job.update({k: v})

                print(job)
                jobs.append(job)

        img_count = len(files) * p.n_iter
        batch_count = math.ceil(img_count / p.batch_size)
        print(f"Will process {img_count} images in {batch_count} batches.")

        state.job_count = batch_count

        images = []
        for i, job in enumerate(jobs):
            copy_p = copy.copy(p)
            state.job = f"{i + 1} out of {state.job_count}"
            for k, v in job.items():
                setattr(copy_p, k, v)

            proc = process_images(copy_p)
            images += proc.images

        return Processed(p, images, p.seed, "")
