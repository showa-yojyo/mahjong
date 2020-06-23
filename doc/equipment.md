---
title: 麻雀プログラム ゲーム環境仕様
---

## 雀卓

全自動卓と手積み卓を実装するものとする。ゲームモードによって使い分ける。

## 点棒

自動卓でも点棒を用いるものとする。点棒の構成は次の通り：

* 一万点棒
* 五千点棒
* 千点棒
* 五百点棒
* 百点棒

点棒の基本的な意匠は、文章で記述するのが至難だ。実装者は実物を見て理解して欲しい。
画面に描画する点棒の本体の色は点の高い順からそれぞれ赤、黄、青、緑、白とする。

東風戦のような配給原点が低いゲームモードでは、未使用の点棒があってよい。
セットアップ仕様を参照。

## 麻雀牌

麻雀牌仕様を参照。

ゲーム中で用いる麻雀牌を標準的な 34 種をそれぞれ 4 枚ずつからなる 136 牌とする。

赤牌は採用しない。

最近の Unicode では麻雀牌のためのコードポイントが割り振られている。
仕様に必要なものを次に示す。

| コード | 牌画 | `unicodedata.name` |
|-------:|------|:-------------------|
| U+1F000 | 🀀 | MAHJONG TILE EAST WIND |
| U+1F001 | 🀁 | MAHJONG TILE SOUTH WIND |
| U+1F002 | 🀂 | MAHJONG TILE WEST WIND |
| U+1F003 | 🀃 | MAHJONG TILE NORTH WIND |
| U+1F004 | 🀄 | MAHJONG TILE RED DRAGON |
| U+1F005 | 🀅 | MAHJONG TILE GREEN DRAGON |
| U+1F006 | 🀆 | MAHJONG TILE WHITE DRAGON |
| U+1F007 | 🀇 | MAHJONG TILE ONE OF CHARACTERS |
| U+1F008 | 🀈 | MAHJONG TILE TWO OF CHARACTERS |
| U+1F009 | 🀉 | MAHJONG TILE THREE OF CHARACTERS |
| U+1F00A | 🀊 | MAHJONG TILE FOUR OF CHARACTERS |
| U+1F00B | 🀋 | MAHJONG TILE FIVE OF CHARACTERS |
| U+1F00C | 🀌 | MAHJONG TILE SIX OF CHARACTERS |
| U+1F00D | 🀍 | MAHJONG TILE SEVEN OF CHARACTERS |
| U+1F00E | 🀎 | MAHJONG TILE EIGHT OF CHARACTERS |
| U+1F00F | 🀏 | MAHJONG TILE NINE OF CHARACTERS |
| U+1F010 | 🀐 | MAHJONG TILE ONE OF BAMBOOS |
| U+1F011 | 🀑 | MAHJONG TILE TWO OF BAMBOOS |
| U+1F012 | 🀒 | MAHJONG TILE THREE OF BAMBOOS |
| U+1F013 | 🀓 | MAHJONG TILE FOUR OF BAMBOOS |
| U+1F014 | 🀔 | MAHJONG TILE FIVE OF BAMBOOS |
| U+1F015 | 🀕 | MAHJONG TILE SIX OF BAMBOOS |
| U+1F016 | 🀖 | MAHJONG TILE SEVEN OF BAMBOOS |
| U+1F017 | 🀗 | MAHJONG TILE EIGHT OF BAMBOOS |
| U+1F018 | 🀘 | MAHJONG TILE NINE OF BAMBOOS |
| U+1F019 | 🀙 | MAHJONG TILE ONE OF CIRCLES |
| U+1F01A | 🀚 | MAHJONG TILE TWO OF CIRCLES |
| U+1F01B | 🀛 | MAHJONG TILE THREE OF CIRCLES |
| U+1F01C | 🀜 | MAHJONG TILE FOUR OF CIRCLES |
| U+1F01D | 🀝 | MAHJONG TILE FIVE OF CIRCLES |
| U+1F01E | 🀞 | MAHJONG TILE SIX OF CIRCLES |
| U+1F01F | 🀟 | MAHJONG TILE SEVEN OF CIRCLES |
| U+1F020 | 🀠 | MAHJONG TILE EIGHT OF CIRCLES |
| U+1F021 | 🀡 | MAHJONG TILE NINE OF CIRCLES |

この他にも花牌等と牌裏の文字が存在する。

Python での応用例としては、例えば "MAHJONG TILE EAST WIND" のような牌名から
動的に牌を意味するクラスを定義することなどが考えられる。
そのときは当然メソッド `__str__()` が `\N{MAHJONG TILE EAST WIND}` を返すように書く。

三元牌についてはコードポイントの順序が白発中とはなっていないので注意する。

### 数牌

数牌とは萬子、筒子、索子各牌の総称である。

#### 萬子

萬子とは次の 9 牌の総称である。牌の表を漢数字と「萬」の字で描くものとする。

* 一萬
* 二萬
* 三萬
* 四萬
* 五萬
* 六萬
* 七萬
* 八萬
* 九萬

五萬について注意。仕様書では「五萬」の表記で統一するものの、
伝統的な理由から、卓上の麻雀牌としての五萬については「五」を「伍」とする。

#### 筒子

筒子とは次の 9 牌の総称である。牌の表を古代の貨幣のようなものの図案で描くものとする。

* 一筒
* 二筒
* 三筒
* 四筒
* 五筒
* 六筒
* 七筒
* 八筒
* 九筒

#### 索子

索子とは次の 9 牌の総称である。牌の表を竹の図案で描くものとする。
一索だけは例外的に鳥（孔雀）の図案を採用するものとする。

* 一索
* 二索
* 三索
* 四索
* 五索
* 六索
* 七索
* 八索
* 九索

### 字牌

字牌とは風牌と三元牌の総称である。

#### 風牌

風牌とは次の 4 牌の総称である：

* 東
* 南
* 西
* 北

#### 三元牌

三元牌とは次の 3 牌の総称である：

* 白
* 発
* 中

白の表面には何も描かれていないものとする。

## 起家マーク

一方に「東」と、他方に「南」と書かれた札を一枚利用する。

東一局の開始までに起家の卓上の枠に「東」の面を上にしておく。
南入時にこれを裏返し、「南」の面を上にする。

## サイコロ

赤と白それぞれのサイコロを一個ずつ計二個用いる。次のようにしか使われない：

```python
import random

(red, white) = (random.randrange(1, 7) for _ in range(2))
nsum = red + white
return nsum, nsum % 4
```

サイコロをモデリングした上で物理演算により転がし、それらの出目を採用してもよい。

## その他

雀卓周辺のスコア表、電卓、座椅子、サイドテーブル等々、画面に映り込むものを適宜モデリングする。
