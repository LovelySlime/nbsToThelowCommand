
import os
import json

def main():
    # --- ユーザー設定（対話形式） ---
    print("--- 設定を入力してください（カッコ内はデフォルト値） ---")

    # .mcfunctionファイルが格納されているディレクトリ
    default_notes_dir = os.path.join("data", "atari", "functions", "notes")
    notes_dir_input = input(f".mcfunctionファイルが格納されているディレクトリ [{default_notes_dir}]: ")
    notes_dir = notes_dir_input if notes_dir_input else default_notes_dir

    # executeコマンドのセレクタ
    default_selector = "@a"
    selector_input = input(f"executeコマンドのセレクタ [{default_selector}]: ")
    selector = selector_input if selector_input else default_selector

    # sequenceLoopExecの遅延秒数
    default_delay_seconds = 0.05
    while True:
        try:
            delay_seconds_input = input(f"sequenceLoopExecの遅延秒数（小数） [{default_delay_seconds}]: ")
            if not delay_seconds_input:
                delay_seconds = default_delay_seconds
                break
            delay_seconds = float(delay_seconds_input)
            break
        except ValueError:
            print("エラー: 正しい数値を入力してください。")

    # --- 固定設定 ---
    config_path = "config.json"
    output_path = "output.txt"

    print("-----------------------------------------------------")

    # --- 処理開始 ---
    print("処理を開始します...")

    # 1. 初期化
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            sound_map = json.load(f)
        print(f"音源定義ファイル '{config_path}' を読み込みました。")
    except FileNotFoundError:
        print(f"エラー: 音源定義ファイル '{config_path}' が見つかりません。")
        return
    except json.JSONDecodeError:
        print(f"エラー: 音源定義ファイル '{config_path}' の形式が正しくありません。")
        return

    unmapped_sounds = set()

    # 2. ファイル収集とソート
    try:
        all_files = os.listdir(notes_dir)
    except FileNotFoundError:
        print(f"エラー: ディレクトリ '{notes_dir}' が見つかりません。")
        return

    mcfunction_files = []
    for filename in all_files:
        # ファイル名が数字のみで構成され、.mcfunctionで終わるかチェック
        if filename.endswith('.mcfunction') and filename.split('.')[0].isdigit():
            # 数値部分を整数として取得
            file_number = int(filename.split('.')[0])
            mcfunction_files.append((file_number, os.path.join(notes_dir, filename)))

    # ファイル名の数値でソート
    mcfunction_files.sort()

    if not mcfunction_files:
        print(f"警告: '{notes_dir}' 内に処理対象の <数値>.mcfunction ファイルが見つかりませんでした。")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("") # 空のファイルを作成
        print(f"処理が完了しました。結果を {output_path} に出力しました。")
        return
        
    print(f"{len(mcfunction_files)}個の .mcfunction ファイルを見つけました。")

    all_sequences = []
    max_file_number = 0

    # 3. element の生成 & 4. sequencecommand の構築
    for file_number, file_path in mcfunction_files:
        max_file_number = max(max_file_number, file_number)
        elements = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if not line.startswith("playsound"):
                    continue

                parts = line.split()
                # parts: ["playsound", "<sound_id>", "record", "@s", "^0", "^", "^", "1", "<pitch>", "1"]
                if len(parts) < 9:
                    continue

                original_sound_id = parts[1]
                pitch = parts[8]

                # sound_idを変換
                new_sound_id = sound_map.get(original_sound_id)
                if new_sound_id is None:
                    unmapped_sounds.add(original_sound_id)
                    new_sound_id = original_sound_id # 見つからなかった場合は元IDをそのまま使う

                # elementを構築
                element = f"execute {selector} ~ ~ ~ playsound {new_sound_id} @.p[r=2] ~ ~ ~ 1 {pitch} 1"
                elements.append(element)

        if elements:
            sequence = " & ".join(elements)
            all_sequences.append((file_number, f"sequencecommand 0 {sequence}"))
        else:
            all_sequences.append((file_number, "")) # 空の場合は空白

    # 5. sequenceLoopExec の構築
    # all_sequencesを辞書に変換して、番号で引けるようにする
    sequence_map = dict(all_sequences)
    final_sequence_parts = []
    # 0から最大のファイル番号までループを回し、歯抜けの番号には空白を挿入する
    for i in range(max_file_number + 1):
        final_sequence_parts.append(sequence_map.get(i, ""))

    final_sequences_str = " ? ".join(final_sequence_parts)
    command_count = max_file_number + 1

    final_command = f"gi sequenceLoopExec {delay_seconds} {command_count} {final_sequences_str}"

    # 6. 出力
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_command)

    # 未マッピングのサウンドがあれば警告を表示
    if unmapped_sounds:
        print("\n--- 警告 ---")
        print(f"以下のサウンドIDが '{config_path}' に見つかりませんでした。元のIDをそのまま使用しました:")
        for sound in sorted(list(unmapped_sounds)):
            print(f"- {sound}")

    print(f"\n処理が完了しました。結果を '{output_path}' に出力しました。")

if __name__ == "__main__":
    main()
