# Captioning Tools
テキストを含む画像のキャプションと画像中に何が書かれているかのアノテーションを行うためのツールです．

#### 必要なパッケージ
- pyqt5

#### 実行方法

```sh
python app.py
```

#### 実装機能
- 選択したフォルダーを開く(Ctrl+o)
  - 選択するディレクトリー（dir）は以下のように構成していること
    <pre>
    dir/
     ├ image/
     ├ text/
     └ label/
    </pre>
    * text/とlabel/はない場合は新しく作成する
- 画像を1枚づつ表示する
  - left-keyで前の画像，right-keyで次の画像に移動
- 作成したアノテーションの保存(Ctrl+s)