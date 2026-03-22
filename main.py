import os
import json

def main():
    # --- ユーザー設定（対話形式） ---
    print("--- 設定を入力してください（カッコ内はデフォルト値） ---")

    default_notes_dir = os.path.join("data", "atari", "functions", "notes")
    notes_dir_input = input(f".mcfunctionファイルが格納されているディレクトリ [{default_notes_dir}]: ")
    notes_dir = notes_dir_input if notes_dir_input else default_notes_dir

    default_selector = "@a"
    selector_input = input(f"executeコマンドのセレクタ [{default_selector}]: ")
    selector = selector_input if selector_input else default_selector

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

    config_path = "config.json"
    output_path = "output.txt"

    print("-----------------------------------------------------")
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
    pitch_warnings = [] # 新規追加：ピッチ補正の警告を格納するリスト

    # 2. ファイル収集とソート
    try:
        all_files = os.listdir(notes_dir)
    except FileNotFoundError:
        print(f"エラー: ディレクトリ '{notes_dir}' が見つかりません。")
        return

    mcfunction_files = []
    for filename in all_files:
        if filename.endswith('.mcfunction') and filename.split('.')[0].isdigit():
            file_number = int(filename.split('.')[0])
            mcfunction_files.append((file_number, os.path.join(notes_dir, filename)))

    mcfunction_files.sort()

    if not mcfunction_files:
        print(f"警告: '{notes_dir}' 内に処理対象の <数値>.mcfunction ファイルが見つかりませんでした。")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("")
        print(f"処理が完了しました。結果を {output_path} に出力しました。")
        return
        
    print(f"{len(mcfunction_files)}個の .mcfunction ファイルを見つけました。")

    all_sequences = []
    max_file_number = 0

    # 3. element の生成 & 4. sequencecommand の構築
    for file_number, file_path in mcfunction_files:
        max_file_number = max(max_file_number, file_number)
        elements = []
        filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()
                if not line.startswith("playsound"):
                    continue

                parts = line.split()
                if len(parts) < 9:
                    continue

                original_sound_id = parts[1]
                pitch_str = parts[8]

                try:
                    original_pitch = float(pitch_str)
                except ValueError:
                    original_pitch = 1.0

                # config.jsonからマッピング情報を取得
                mapping_data = sound_map.get(original_sound_id)
                new_sound_id = original_sound_id
                pitch_multiplier = 1.0

                if isinstance(mapping_data, str):
                    # 従来の文字列での指定（倍率は1.0）
                    new_sound_id = mapping_data
                elif isinstance(mapping_data, dict):
                    # 辞書型での指定（IDと倍率を取得）
                    new_sound_id = mapping_data.get("id", original_sound_id)
                    pitch_multiplier = mapping_data.get("pitch_multiplier", 1.0)
                elif mapping_data is None:
                    unmapped_sounds.add(original_sound_id)

                # ピッチの計算とオクターブ調整
                calculated_pitch = original_pitch * pitch_multiplier
                adjusted_pitch = calculated_pitch
                octave_shifts = 0

                # 2.0を超える場合は、0.5〜2.0に収まるまで半分（1オクターブ下げ）にする
                while adjusted_pitch > 2.0:
                    adjusted_pitch /= 2.0
                    octave_shifts -= 1
                
                # 0.5未満の場合は、0.5〜2.0に収まるまで2倍（1オクターブ上げ）にする
                # （※エラー回避のため、adjusted_pitchが0以下の場合は処理しない）
                while adjusted_pitch < 0.5 and adjusted_pitch > 0:
                    adjusted_pitch *= 2.0
                    octave_shifts += 1

                # 補正が行われた場合、警告リストに追加
                if octave_shifts != 0:
                    shift_dir = "下げ" if octave_shifts < 0 else "上げ"
                    pitch_warnings.append(
                        f"  - [{filename}] {original_sound_id}: 計算値 {calculated_pitch:.3f} -> {adjusted_pitch:.3f} に補正 ({abs(octave_shifts)}オクターブ{shift_dir})"
                    )

                # ピッチを文字列化（無駄な小数点の0を省く）
                final_pitch_str = f"{adjusted_pitch:.3f}".rstrip('0').rstrip('.')
                if final_pitch_str == "": 
                    final_pitch_str = "0"

                # elementを構築
                element = f"execute {selector} ~ ~ ~ playsound {new_sound_id} @.p[r=2] ~ ~ ~ 1 {final_pitch_str} 1"
                elements.append(element)

        if elements:
            sequence = " & ".join(elements)
            all_sequences.append((file_number, f"sequencecommand 0 {sequence}"))
        else:
            all_sequences.append((file_number, ""))

    # 5. sequenceLoopExec の構築
    sequence_map = dict(all_sequences)
    final_sequence_parts = []
    for i in range(max_file_number + 1):
        final_sequence_parts.append(sequence_map.get(i, ""))

    final_sequences_str = " ? ".join(final_sequence_parts)
    command_count = max_file_number + 1

    final_command = f"gi sequenceLoopExec {delay_seconds} {command_count} {final_sequences_str}"

    # 6. 出力
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_command)

    # --- 警告の表示 ---
    if unmapped_sounds or pitch_warnings:
        print("\n--- 警告・通知 ---")

    if unmapped_sounds:
        print(f"【未マッピング】以下のIDが '{config_path}' に見つかりませんでした:")
        for sound in sorted(list(unmapped_sounds)):
            print(f"  - {sound}")
        print() # 空行

    if pitch_warnings:
        print("【ピッチ自動補正】一部のピッチが0.5〜2.0の範囲外だったため、オクターブ調整を行いました:")
        for warning in pitch_warnings:
            print(warning)

    print(f"\n処理が完了しました。結果を '{output_path}' に出力しました。")

if __name__ == "__main__":
    main()