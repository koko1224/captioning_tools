# Captioning Tools
テキストを含む画像のキャプションと画像中に何が書かれているかのアノテーションを行うためのツールです．

#### 必要なパッケージ
- pyqt5

#### 準備
```sh
pip install -r requirements.txt
```

#### 実行方法

```sh
cd path/to/captioning_tool
python app.py
```

#### 実装機能
- 選択したフォルダーを開く(Ctrl+o)
  - 選択するディレクトリー（dataset/）は以下のように構成していること
    <pre>
    dataset/
      ┠ image/
      ┃  ┠ train/
      ┃  ┗ test/
      ┠ text/
      ┃ ┠ train/
      ┃ ┗ test/
      ┗ label/
        ┠ train/
        ┗ test/
    </pre>
    もしくは
    <pre>
    dataset/
      ┠ image/
      ┠ text/
      ┗ label/
    </pre>
    * text/ と label/については，存在しない場合image/に合わせて新しく作成される
- 画像を表示
  - left-keyで前の画像，right-keyで次の画像に移動
- 作成したアノテーションの保存(Ctrl+s)
- 選択した画像にジャンプ
- アノテーションのオンオフ
  - テキストのアノテーションが存在する場合表示させることができる
  - メニューバーViewのtoggle annotation もしくはCtrl+Tで切り替え
