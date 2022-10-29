# ライブラリの読み込み 関数の定義
from apiclient.discovery import build
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import subprocess
from subprocess import PIPE
import csv

# ここに自分のAPIキーを入力
YOUTUBE_API_KEY = 'Your API Key'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


def get_video_info(part, q, order, type, num):
    dic_list = []
    search_response = youtube.search().list(part=part, q=q, order=order, type=type)
    output = youtube.search().list(part=part, q=q, order=order, type=type).execute()

    # 一度に5件しか取得できないため何度も繰り返して実行
    for i in range(num):
        dic_list = dic_list + output['items']
        search_response = youtube.search().list_next(search_response, output)
        output = search_response.execute()

    df = pd.DataFrame(dic_list)
    # 各動画毎に一意のvideoIdを取得
    df1 = pd.DataFrame(list(df['id']))['videoId']
    # 各動画毎に一意のvideoIdを取得必要な動画情報だけ取得
    df2 = pd.DataFrame(list(df['snippet']))[
        ['channelTitle', 'publishedAt', 'channelId', 'title', 'description']]
    ddf = pd.concat([df1, df2], axis=1)
    return ddf


def get_contents_detail_core(youtube, videoids):
    '''動画の詳細情報を取得'''
    part = ['snippet', 'contentDetails']
    response = youtube.videos().list(part=part, id=videoids).execute()
    results = []
    for item in response['items']:
        info = get_basicinfo(item)
        info['duration'] = get_duration(item)
        results.append(info)
    return pd.DataFrame(results)


def get_contents_detail(youtube, videoids):
    '''必要に応じて50件ずつにIDを分割し、詳細情報を取得'''
    n_req_pre_once = 50

    # IDの数が多い場合は50件ずつ動画IDのリストを作成
    if len(videoids) > n_req_pre_once:
        videoids_list = np.array_split(
            videoids, len(videoids) // n_req_pre_once + 1)
    else:
        videoids_list = [videoids, ]

    # 50件ずつ動画IDのリストを渡し、動画の詳細情報を取得
    details_list = []
    for vids in videoids_list:
        df_video_details_part =\
            get_contents_detail_core(youtube, vids.tolist())
        details_list.append(df_video_details_part)

    df_video_details =\
        pd.concat(details_list, axis=0).reset_index(drop=True)
    return df_video_details


def get_duration(item):
    '''動画時間を抜き出す（ISO表記を秒に変換）'''
    content_details = item['contentDetails']
    pt_time = content_details['duration']
    return pt2sec(pt_time)


def get_basicinfo(item):
    '''動画の基本情報の抜き出し'''
    basicinfo = dict(id=item['id'])
    # snippets
    keys = ('title', 'description', 'channelTitle')
    snippets = {k: item['snippet'][k] for k in keys}
    basicinfo.update(snippets)
    return basicinfo


def pt2sec(pt_time):
    '''ISO表記の動画時間を秒に変換 '''
    pttn_time = re.compile(r'PT(\d+H)?(\d+M)?(\d+S)?')
    keys = ['hours', 'minutes', 'seconds']
    m = pttn_time.search(pt_time)
    if m:
        kwargs = {k: 0 if v is None else int(v[:-1])
                  for k, v in zip(keys, m.groups())}
        return timedelta(**kwargs).total_seconds()
    else:
        msg = '{} is not valid ISO time format.'.format(pt_time)
        raise ValueError(msg)


def get_csv_data(filename):
    # ./hand_play.csvを一行ずつ読み込む
    video_list = []
    video_id_list = []

    with open(filename, "r", encoding="utf8") as csv_file:
        # リスト形式
        video_list = csv.reader(csv_file)
        for element in video_list:
            video_id_list.append(element[1])

    # video_id_listの'id'を削除
    video_id_list.pop(0)
    return video_id_list


def download_video(video_id_list):
    for video_id in video_id_list:
        # heightダウンロードできるサイズであれば自由に変更可能
        # -Pでパスを指定
        # ここではカレントディレクトリの下のyoutube_videosディレクトリにダウンロードする
        url_command = "yt-dlp -P './youtube_videos' -f 'bv[height=720][ext=mp4]+ba[ext=m4a]' --merge-output-format mp4 " + \
            "'https://www.youtube.com/watch?v=" + video_id + "'"

        sub_proc = subprocess.run(url_command, shell=True, stdout=PIPE)
        print("-----")
        print(sub_proc)


if __name__ == "__main__":
    # 関数を実行して結果をデータフレームに保存
    # qに検索したいキーワードを入力
    df = get_video_info(part='snippet', q='検索したいキーワードを入力',
                        order='viewCount', type='video', num=5)

    # 動画ID
    videoids = df['videoId'].values

    # 動画の詳細情報を取得
    df_video_details = get_contents_detail(youtube, videoids)

    # 再生時間がx時間以上、x時間以下の動画に絞り込む
    lower_duration = 60 * 60  # 1時間以上
    upper_duration = 600 * 60  # 10時間以下
    is_matched = df_video_details['duration'].between(
        lower_duration, upper_duration)

    df_video_playlist = df_video_details.loc[is_matched, :]

    # csvファイルに出力
    # 自由に名前変更可能
    # キーワード検索で得たデータをxxx.csvに格納
    df.to_csv("xxx.csv")
    # xxx.csvに格納された動画の詳細データ
    df_video_details.to_csv("xxx_details.csv")
    # 上記のis_matchedで再生時間フィルタがかけられたデータをxxx_filtering.csvに保存
    df_video_playlist.to_csv("xxx_filtering.csv")

    # フィルタがかけられたデータを指定
    filename = "xxx_filtering.csv"

    # 動画IDのリストを取得
    video_id_list = get_csv_data(filename)

    # デバッグ用
    print(video_id_list)

    # 動画のダウンロード
    download_video(video_id_list)
