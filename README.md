# NBS -> Thelow Comamnd Translator

Minecraft Java 1.8.9 - TheLowプラグイン環境専用の、コマンド生成スクリプトです。

## 主な機能
Note Block Studioで完成させた音楽を、ぱっとThelowで実行できるコマンド形式に変換することができます。
Bellなどの1.8.9にないコマンドでも、変換ファイルに定義することで1.8.9に存在する音に変換できます。
pitch差がある音(bell(pitch 1.0 = ファ#) → random.orb(pitch 1.0 = ミ♭))に関しても、pitch倍率を定義ファイルに記載することでpitchが合わせられます。

読んでも使用方法がわからない場合は、気軽に開発鯖でメンションしてください。

---

## 使い方

### 1. 準備
・Note Block Studio からの書き出し
Note Block Studioの左上のFileから、export as data packを選択します。左上の入力boxに適当な名前を付けて保存します。

・pythonのダウンロード
https://www.python.org/downloads/ の黄色いボタンからpythonをダウンロードし、導入まで行ってください。導入中の、Path~みたいなことを書いてる設定を、必ずonにしてください。

・ここのファイルのダウンロード
緑色のCodeボタンから、Download ZIPをクリックしダウンロードします。展開しておいてください。

### 2. 設定ファイルの準備 (`config.json`)
変換元のサウンドIDと、変換先のサウンドID（およびピッチ補正値）を設定します。

設定方法は以下の2通りを混在させることができます。

**A. IDのみを変換する場合（ピッチ補正なし）**
従来通り、変換先IDを文字列で指定します。
```json
{
  "block.note_block.harp": "note.harp"
}
```

**B. ID変換 ＋ ピッチ補正を行う場合**
辞書形式（`{}`）で指定し、`id` に変換先サウンドIDを、`pitch_multiplier` にピッチの補正倍率を指定します。
```json
{
  "block.note_block.bass": {
    "id": "custom.sound.eb",
    "pitch_multiplier": 1.1892
  }
}
```
*※補足: Minecraftの1半音は `2^(1/12) ≒ 1.05946` 倍です。基準音（ピッチ1.0 = ファ#）からズレている音源を使用する際の計算に利用してください。わからなければChatGPTとかに聞いたら数秒で終わります。*

### 3. スクリプトの実行
付属の

実行すると、ターミナル上で以下の設定が求められます。そのままEnterを押すと [ ] 内のデフォルト値が適用されます。
1. **.mcfunctionファイルが格納されているディレクトリ:** （デフォルト: `data/atari/functions/notes`）
2. **executeコマンドのセレクタ:** （デフォルト: `@a`）
3. **sequenceLoopExecの遅延秒数:** （デフォルト: `0.05`）★Note Block Studioの左上のxx.xxt / s 表示を見てください！1/xx.xxの値を記載してください。

### 4. 出力の確認
処理が完了すると、スクリプトと同じディレクトリに `output.txt` が生成されます。
中には以下のような1行のコマンドが出力されています。

```text
gi sequenceLoopExec 0.05 100 sequencecommand 0 execute @a ~ ~ ~ playsound ... ? sequencecommand ...
```

**警告メッセージについて**
実行時、ターミナルに以下のような警告が表示されることがあります。
* **【未マッピング】**: `config.json` に定義されていないサウンドIDが見つかった場合（元のIDがそのまま使用されます）。
* **【ピッチ自動補正】**: ピッチが0.5未満、または2.0を超えたため、自動的にオクターブ調整（0.5〜2.0の範囲への丸め込み）が行われた箇所とそのファイル名。

---

## 必須環境
* Python 3.x
