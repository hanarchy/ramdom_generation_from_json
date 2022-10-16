Random Choice Script
====

AUTOMATIC1111/stable-diffusion-webui用スクリプト。

promptやCFG Scaleなどの調整幅などが記載されたjsonファイルを複数読み込んでランダムで実行。

Generate Foreverと併せてどうぞ。

## Installation

1. `random_generation_from_json.py`をwebui直下の`scripts`フォルダに入れる。
2. webui直下に`prompts`フォルダを作成。
3. `prompts`にプロンプト定義ファイル`*.json`を格納
4. webuiを再起動

## Example

`chino.json`
```json
{
  "image_sizes": [[512,512], [640, 640], [640, 384]],
  "min_cfg_scale": 10,
  "max_cfg_scale": 15,
  "min_steps": 20,
  "max_steps": 40,
  "prompt": "kafuu chino, explosion, chibi, starbucks",
  "negative_prompt": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,artist name, variations, costume chart, multiple views"
}

```

これ以外のパラメータは`modules/processing.py`参照。