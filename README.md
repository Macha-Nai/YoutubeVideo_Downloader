# Youtubeでキーワード検索した動画をPCにダウンロードするプログラム
## 事前準備
### Homebrewを使うのでインストールしてない人はインストール
    https://brew.sh/index_ja
### pipを使うのでインストールしてない人はインストール
    https://qiita.com/ohbashunsuke/items/e7c673db606a6dced8a6<br>
### pipでpandasを入れる
    pip install pandas
### pipでgoogle-api-python-clientを入れる
    pip install google-api-python-client
- その他importの部分でエラー吐かれたら自分でインストールしてください
### yt-dlpのインストール(動画のダウンロードに使用)
  
### Youtubeでキーワード検索するためのAPIキー取得
  
## キーワード検索した動画のダウンロード
- Youtube Data API v3は使用回数に厳しい制限があるため注意してください
- コードは1日一回か二回しか実行できないため、実行する前に検索キーワードと何本の動画をダウンロードするのか良く考えておいてください

### 実行の前に自分で行うこと
- 変数qに検索したいキーワードを入力する
- 一回のキーワード検索で変数num×5本の動画を取ってこれる（これ以上数値を上げるのはおすすめしない）
- YOUTUBE_API_KEYに自分が取得したAPIキーを入力する
- 用途に合わせてcsv形式のファイル名を指定する

### コードを実行すると自動的にダウンロードされる
    python3 YoutubeDownloader.py

## Youtube Data API v3では他にも色々な使い道があるので興味がある方は調べてみてください。
- 繰り返しになりますが、Youtube Data API v3は使用回数に厳しい制限があるので注意してください
- どの程度使用可能かはサイトで確認してください
- 使用回数の上限に達するとコードを実行できません
