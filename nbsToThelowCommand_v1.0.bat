@echo off
setlocal enabledelayedexpansion

:: ユーザー入力
set /p endNumber=mcfunctionの最大数値を入力してください (0 から n の範囲): 
set /p delayms=遅延倍率(ms)を入力してください。:
set /p mode=モードを選択してください。0-locate,1-execute:
if "%mode%"=="0" (
    set /p locateX=X座標を入力してください。:
    set /p locateY=Y座標を入力してください。:
    set /p locateZ=Z座標を入力してください。:
    set /p selector=セレクターを入力してください。:
)
if "%mode%"=="1" (
    set /p selector=セレクターを入力してください。:
)

:: 結果ファイルの初期化
> result.txt echo.

:: 初期のシーケンスコマンド
echo sequencecommand 0 >> result.txt

:: 0から指定数値までのループ
for /l %%x in (0,1,%endNumber%) do (
    set "fileName=%%x.mcfunction"

    :: ファイル確認
    if exist "!fileName!" (
        set "outputLine="

        :: 行解析
        for /f "tokens=1-10 delims= " %%a in (!fileName!) do (
            if "%%a"=="playsound" (
                set "element2=%%b"
                set "delay=%%x"

                :: サウンド名の置換
                if "!element2!"=="minecraft:block.note_block.harp" set "element2=note.harp"
                if "!element2!"=="minecraft:block.note_block.bass" set "element2=note.bass"
                if "!element2!"=="minecraft:block.note_block.basedrum" set "element2=note.bd"
                if "!element2!"=="minecraft:block.note_block.hat" set "element2=note.hat"
                if "!element2!"=="minecraft:block.note_block.snare" set "element2=note.snare"
                if "!element2!"=="minecraft:block.note_block.pling" set "element2=note.pling"
                if "!element2!"=="minecraft:block.note_block.click" set "element2=random.pling"
                if "!element2!"=="minecraft:block.note_block.bit" set "element2=random.anvil_land"

                :: 遅延時間の計算
                set /a sA=!delayms!*%%x
				set /a sB=!sA!/1000
				set /a sC=!sA!%%1000
				set "finalDelay=!sB!.!sC!"
				
                set "processedLine=delaycommand !finalDelay! execute !selector! ~ ~ ~ %%a !element2! !selector! ~ ~ ~ 1 %%i 1 & "

                :: 出力行の更新
                if defined outputLine (
                    set "outputLine=!outputLine!!processedLine!"
                ) else (
                    set "outputLine=!processedLine!"
                )
            )
        )

        :: 結果ファイルへの書き込み
        if defined outputLine (
            echo !outputLine! >> result.txt
        )
    )
)

echo 結果が result.txt に出力されました。
pause
endlocal
