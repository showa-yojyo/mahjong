---
title: 麻雀プログラム 麻雀牌仕様
---

## 概要

ゲーム中で用いる麻雀牌を標準的な 34 種をそれぞれ 4 枚ずつからなる 136 牌とする。

赤牌は採用しない。

## 麻雀牌を表す Unicode 文字表

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

## 牌の構成

### 数牌

数牌とは萬子、筒子、索子各牌の総称である。

#### 萬子

萬子とは次の 9 牌の総称である。牌の表を漢数字と「萬」の字で描くものとする。

TBW

五萬について注意。仕様書では「五萬」の表記で統一するものの、
伝統的な理由から、卓上の麻雀牌としての五萬については「五」を「伍」とする。

#### 筒子

筒子とは次の 9 牌の総称である。牌の表を古代の貨幣のようなものの図案で描くものとする。

TBW

#### 索子

索子とは次の 9 牌の総称である。牌の表を竹の図案で描くものとする。
一索だけは例外的に鳥（孔雀）の図案を採用するものとする。

TBW

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

## 理牌

プレイヤーの便宜を図るため自動理牌を実装するものとする。
このオプションが有効なときには、配牌直後および手番の直後に自動的に手牌が理牌されるものとする。

萬子・筒子・索子・風牌・三元牌をグループ化し、それぞれのグループ内でソートするものとする。
このグループの順序はシステムが勝手に決めてよい。
配牌中に所属グループが出現する順序と一致させるのが自然だろう。

ソートには Unicode のコードポイントを援用してよい（ただし三元牌は注意）。
