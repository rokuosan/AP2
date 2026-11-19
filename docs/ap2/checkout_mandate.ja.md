# Checkout Mandate

> このページは AP2 ドキュメントの非公式日本語訳です。
> [英語の原文を読む](https://github.com/google-agentic-commerce/AP2/blob/main/docs/ap2/checkout_mandate.md)

Checkout Mandate は、チェックアウトの完了を認可するための Mandate です。

## 用途

Shopping Agent が Checkout Mandate の内容を作成し、Trusted Surface がユーザーに表示し、販売者が検証します。販売者は署名付き Checkout オブジェクトを作成し、クローズドな Checkout Mandate の内容に含めます。

## 型

クローズドな Checkout Mandate の `vct` クレームには `mandate.checkout.1`、オープンな Checkout Mandate には `mandate.checkout.open.1` を指定しなければなりません。バージョン接尾辞の仕組みは[Mandate のバージョン](specification.md)を参照してください。

## Mandate スキーマ

クローズドな Checkout Mandate は次のスキーマに適合します。

{{ schema_fields('checkout_mandate', 'ap2', show_sd=True) }}

`checkout_hash` は `checkout_jwt` の値のハッシュを base64url エンコードした値です。使用するアルゴリズムは、基本ペイロードの `_sd_alg` クレームで指定された SD-JWT のアルゴリズムと同じでなければなりません。指定がない場合は `sha-256` を使います。

`checkout_jwt` はチェックアウトの詳細を含む販売者署名付き JWT です。ペイロードの詳細はこの仕様の対象外です。Universal Commerce Protocol と組み合わせる場合は Checkout オブジェクトでなければなりません。

## 制約

この文書では、オープンな Checkout Mandate で使う次の制約を定義します。

- **許可された販売者**：この Checkout Mandate を利用できる販売者を制限します。
- **明細項目**：Checkout に含められる明細項目の集合を定めます。

### 許可された販売者

**型**：`checkout.allowed_merchants`

**説明**：この Checkout Mandate を利用できる販売者を制限します。

**プロパティ**：

{{ schema_fields('open_checkout_mandate', 'ap2', show_sd=True,
pointer='#/$defs/allowed_merchants') }}

**評価**：販売者は `allowed` の開示された要素に含まれていなければなりません。販売者が含まれない場合、または `allowed` に開示された要素がない場合、この制約は無効です。

**例**

```json
{
  "type": "checkout.allowed_merchants",
  "allowed": [
    {"name": "Merchant Choice", "website": "https://merchant-choice.com"},
    {"name": "Second Merchant", "website": "https://second-merchant.com"}
  ]
}
```

### 明細項目

**型**：`checkout.line_items`

**説明**：`checkout_jwt` に含められる明細項目の集合を定めます。

**プロパティ**：

{{ schema_fields('open_checkout_mandate', 'ap2', show_sd=True,
pointer='#/$defs/line_items') }}

**評価**：次の条件がすべて満たされるとき、この制約を満たします。

- 制約の各 `items` エントリーについて、Checkout 内に一致する項目が指定数量分存在します。
- 項目の ID が開示された `acceptable_items` に含まれる場合、その項目は `items` エントリーと一致します。
- 同じ `items` エントリーまたは Checkout 内の項目を複数回使うことはできません。

最大フロー問題として実装できます。グラフを次のように定義します。

1. `items` エントリーごとにノードを作ります。
2. 始点から各 `items` ノードに、数量を容量とする辺を作ります。
3. Checkout 内の各項目 ID にノードを作ります。
4. Checkout の各項目ノードから終点に、その項目 ID の合計数量を容量とする辺を作ります。
5. 開示された `acceptable_items` と一致する各 `items` ノードと Checkout 項目ノードの間に、無限容量の辺を作ります。

最大フローが制約側の `items` の合計数量と Checkout 側の `items` の合計数量の両方に等しい場合、制約を満たします。

> 注：この評価方法は、1つのオープンな Checkout Mandate を複数の Checkout に分割して使うことに対応していません。将来の制約拡張で対応できますが、重複注文をどう防ぐか検討が必要です。

**例**

```json
{
  "type": "checkout.line_items",
  "items": [
    {
      "id": "id-shoe-choices",
      "acceptable_items": [
        {"id": "BAB1234", "title": "Red Style"},
        {"id": "FAF1234", "title": "Blue Style"}
      ],
      "quantity": 1
    },
    {
      "id": "id-sock-choices",
      "acceptable_items": [
        {"id": "QRT1234", "title": "The Best Socks"}
      ],
      "quantity": 1
    }
  ]
}
```

次の組み合わせは制約を満たします。

- Red Style と The Best Socks
- Blue Style と The Best Socks

一方、Checkout に次の項目が含まれる場合は無効です。

- Red Style と Blue Style
- Red Style のみ
- Blue Style のみ
- The Best Socks のみ

## Checkout Receipt

Checkout Receipt は次のスキーマに適合します。

{{ schema_fields('checkout_receipt', 'ap2', show_sd=True) }}

## 例

### オープンな Checkout Mandate の SD-JWT と開示情報

次の例は、オープンな Checkout Mandate とその開示情報を SD-JWT で表します。JSON のプロパティ名、クレーム、値はプロトコル上のデータなので、原文のまま記載します。

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "example+sd-jwt",
      "kid": "agent-provider-key-1"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "QtXTJtWqg999CmUWGjHFTWMkRPguDfeK3wGSaInd-dw"
        }
      ],
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "y3aocAD2rhYpJQOUMN016faDFGkTBGEDVl1R1TRHdbw",
      "decoded": [
        "4n3L_-3_Fm2GgyFAF8Ct_g",
        {
          "id": "supershoe_limited_edition_gold_sneaker_womens_9_0",
          "title": "SuperShoe Limited Edition Gold"
        }
      ]
    },
    {
      "digest": "a5UMAdxCk_MRayyVdRhpIAZ0ZhjVLEq1g2BWyruKUwg",
      "decoded": [
        "2zPL6vqLBg2WYAdbW9-1lQ",
        {
          "id": "merchant_1",
          "name": "Demo Merchant",
          "website": "https://demo-merchant.example"
        }
      ]
    },
    {
      "digest": "QtXTJtWqg999CmUWGjHFTWMkRPguDfeK3wGSaInd-dw",
      "decoded": [
        "laAoWKNRuGnwREjJWYJ7pg",
        {
          "vct": "mandate.checkout.open.1",
          "constraints": [
            {
              "type": "checkout.line_items",
              "items": [
                {
                  "id": "line_1",
                  "acceptable_items": [
                    {
                      "...": "y3aocAD2rhYpJQOUMN016faDFGkTBGEDVl1R1TRHdbw"
                    }
                  ],
                  "quantity": 1
                }
              ]
            },
            {
              "type": "checkout.allowed_merchants",
              "allowed": [
                {
                  "...": "a5UMAdxCk_MRayyVdRhpIAZ0ZhjVLEq1g2BWyruKUwg"
                }
              ]
            }
          ],
          "cnf": {
            "jwk": {
              "crv": "P-256",
              "kty": "EC",
              "x": "QpSyxPQHy38xckypDr54gZ3T42zj9iLtV4koyb5U27c",
              "y": "37HLd7JJinxjJIn8J7HijssoeclbfhdW-gUL7feI9lw"
            }
          },
          "iat": 1777342357,
          "exp": 1777345957
        }
      ]
    }
  ]
}
```

#### エンコード済みトークン

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImV4YW1wbGUrc2Qtand0IiwgImtpZCI6ICJhZ2VudC1wcm92aWRlci1rZXktMSJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIlF0WFRKdFdxZzk5OUNtVVdHakhGVFdNa1JQZ3VEZmVLM3dHU2FJbmQtZHcifV0sICJfc2RfYWxnIjogInNoYS0yNTYifQ.HvCGk7ye_c0LN2-NFG13wfyu3LA--rckTPGm36ugO2aRvsded7ngw1py8W3JF7wBpoQnsKr17tNTF3zLeYcoWA~WyI0bjNMXy0zX0ZtMkdneUZBRjhDdF9nIiwgeyJpZCI6ICJzdXBlcnNob2VfbGltaXRlZF9lZGl0aW9uX2dvbGRfc25lYWtlcl93b21lbnNfOV8wIiwgInRpdGxlIjogIlN1cGVyU2hvZSBMaW1pdGVkIEVkaXRpb24gR29sZCJ9XQ~WyIyelBMNnZxTEJnMldZQWRiVzktMWxRIiwgeyJpZCI6ICJtZXJjaGFudF8xIiwgIm5hbWUiOiAiRGVtbyBNZXJjaGFudCIsICJ3ZWJzaXRlIjogImh0dHBzOi8vZGVtby1tZXJjaGFudC5leGFtcGxlIn1d~WyJsYUFvV0tOUnVHbndSRWpKV1lKN3BnIiwgeyJ2Y3QiOiAibWFuZGF0ZS5jaGVja291dC5vcGVuLjEiLCAiY29uc3RyYWludHMiOiBbeyJ0eXBlIjogImNoZWNrb3V0LmxpbmVfaXRlbXMiLCAiaXRlbXMiOiBbeyJpZCI6ICJsaW5lXzEiLCAiYWNjZXB0YWJsZV9pdGVtcyI6IFt7Ii4uLiI6ICJ5M2FvY0FEMnJoWXBKUU9VTU4wMTZmYURGR2tUQkdFRFZsMVIxVFJIZGJ3In1dLCAicXVhbnRpdHkiOiAxfV19LCB7InR5cGUiOiAiY2hlY2tvdXQuYWxsb3dlZF9tZXJjaGFudHMiLCAiYWxsb3dlZCI6IFt7Ii4uLiI6ICJhNVVNQWR4Q2tfTVJheXlWZFJocElBWjBaaGpWTEVxMWcyQld5cndLVXdnIn1dfV0sICJjbmYiOiB7Imp3ayI6IHsiY3J2IjogIlAtMjU2IiwgImt0eSI6ICJFQyIsICJ4IjogIlFwU3l4UFFIeTM4eGNreXZEcjU0Z1ozVDQyemo5aUx0VjRrb3liNVUyN2MiLCAieSI6ICIzN0hMZDdKSmlueGpKSW44SjdIaWpzc29lY0JsZmhkVy1nVUw3ZmVJOWx3In19LCAiaWF0IjogMTc3NzM0MjM1NywgImV4cCI6IDE3NzczNDU5NTd9XQ~
```

### クローズドな Checkout Mandate の SD-JWT と開示情報

クローズドな Mandate は特定の Checkout に結び付けられます。`checkout_hash` と必要な開示情報を用いて販売者が内容を検証します。

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "kb+sd-jwt"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "7VLY-eKTFSShLoZRXY5jXcD2UHm1JvPmoANYRqqxy34"
        }
      ],
      "iat": 1777342376,
      "aud": "merchant",
      "nonce": "b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4",
      "sd_hash": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8",
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8",
      "decoded": [
        "w-n1leFT6z8rHTNHwr5Wow",
        "checkout_jwt",
        {
          "header": {
            "alg": "ES256",
            "typ": "JWT"
          },
          "payload": {
            "order_id": "09414145-b7bi-432e-bf5c-ha0ba0bc4580",
            "merchant": {
              "id": "merchant_1",
              "name": "Demo Merchant",
              "website": "https://demo-merchant.example"
            },
            "line_items": [
              {
                "id": "line_1",
                "product": {
                  "id": "supershoe_limited_edition_gold_sneaker_womens_9_0",
                  "title": "SuperShoe Limited Edition Gold — Women's 9",
                  "price": 199.0,
                  "currency": "USD"
                },
                "quantity": 1
              }
            ],
            "total_price": 199.0,
            "currency": "USD",
            "shipping_policy": "Standard Shipping",
            "return_policy": "30-day returns"
          }
        }
      ]
    },
    {
      "digest": "7VLY-eKTFSShLoZRXY5jXcD2UHm1JvPmoANYRqqxy34",
      "decoded": [
        "szhpxKrgGJwyqMEN9WI5Sw",
        {
          "_sd": [
            "3A9UyZJofw2eMP-Lx2tYaNpCcuB8elnhwwLhZLwqFFM"
          ],
          "vct": "mandate.checkout.1",
          "checkout_hash": "NivWhuqfzcvZNapvIEJ2-3tsdQLkiuIcye2g46WVgX8"
        }
      ]
    }
  ]
}
```

#### エンコード済みトークン

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImtiK3NkLWp3dCJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIjdWTFktZUtURlNTaExvWlJYWTVqWGNEMlVIbTFKdlBtb0FOWVJxcXh5MzQifV0sICJpYXQiOiAxNzc3MzQyMzc2LCAiYXVkIjogIm1lcmNoYW50IiwgIm5vbmNlIjogImI5YzhkN2U2ZjVhNGIzYzJkMWUwZjlhOGI3YzZkNWU0IiwgInNkX2hhc2giOiAiRnpMb3hiYnRnUUdZWnhvU00yTkpZSnRrRlRTc2RmVUJvVkVRMTJrN0pOOCIsICJfc2RfYWxnIjogInNoYS0yNTYifQ.lSjkli6K3NbKlWOl1gJdWDwiyL88yJVyx32ZJHmvCXfRoItnchXw-MLUDEJv7o9lmTeipS42qNt7Z_oGSnRH1w~WyJzeGhweEtyZ0dKd3lxTUVNOVdJNVN3IiwgeyJfc2QiOiBbIjNBOVV5WkpvZncyZU1QLUx4MnRZYU5wQ2N1QjhlbG5od3dMaFpMd3FRRk0iXSwgInZjdCI6ICJtYW5kYXRlLmNoZWNrb3V0LjEiLCAiY2hlY2tvdXRfaGFzaCI6ICJOaXZXaHVxZnpjdlpOYXB2SUVKMi0zdHNkUUxraXVJY3llMmc0NldWZ1g4In1d~WyJ3LW4xbGVGVDZ6OHJIVE5Id3I1V293IiwgImNoZWNrb3V0X2p3dCIsICJleUpoYkdjaU9pQWlSVk15TlRZaUxDQWlkSGx3SWpvZ0lrcFhWQ0lzSUNKcmFXUWlPaUFpYldWeVkyaGhiblF0YTJWNUxURWlmUS5leUpwWkNJNklDSXdPVFF4TkRFME5TMWlOekJpTFRRNE0yRXRZamcxWXkxaFlUQm1ZVEJqTkRVNE1EQWlMQ0FpYldWeVkyaGhiblFpT2lCN0ltbGtJam9nSW0xbGNtTm9ZVzUwWHpFaUxDQWlibUZ0WlNJNklDSkVaVzF2SUUxbGNtTm9ZVzUwSWl3Z0luZGxZbk5wZEdVaU9pQWlhSFIwY0hNNkx5OWtaVzF2TFcxbGNtTm9ZVzUwTG1WNFlXMXdiR1VpZlN3Z0lteHBibVZmYVhSbGJYTWlPaUJiZXlKcFpDSTZJQ0pzYVY4d0lpd2dJbWwwWlcwaU9pQjdJbWxrSWpvZ0luTjFjR1Z5YzJodlpWOXNhVzFwZEdWa1gyVmthWFJwYjI1ZloyOXNaRjl6Ym1WaGEyVnlYM2R2YldWdWMxODVYekFpTENBaWRHbDBiR1VpT2lBaVUzVndaWEp6YUc5bElFeHBiV2wwWldRZ1JXUnBkR2x2YmlCSGIyeGtJRk51WldGclpYSWdWMjl0Wlc1eklEa2lMQ0FpY0hKcFkyVWlPaUF4T1Rrd01IMHNJQ0p4ZFdGdWRHbDBlU0k2SURFc0lDSjBiM1JoYkhNaU9pQmJleUowZVhCbElqb2dJbk4xWW5SdmRHRnNJaXdnSW1GdGIzVnVkQ0k2SURFNU9UQXdmU3dnZXlKMGVYQmxJam9nSW5SdmRHRnNJaXdnSW1GdGIzVnVkQ0k2SURFNU9UQXdmVjE5WFN3Z0luTjBZWFIxY3lJNklDSnBibU52YlhCc1pYUmxJaXdnSW1OMWNuSmxibU41SWpvZ0lsVlRSQ0lzSUNKMGIzUmhiSE1pT2lCYmV5SjBlWEJsSWpvZ0luTjFZblJ2ZEdGc0lpd2dJbUZ0YjNWdWRDSTZJREU1T1RBd2ZTd2dleUowZVhCbElqb2dJblJ2ZEdGc0lpd2dJbUZ0YjNWdWRDSTZJREU1T1RBd2ZWMHNJQ0pzYVc1cmN5STZJRnQ3SW5SNWNHVWlPaUFpY0hKcGRtRmplVjl3YjJ4cFkza2lMQ0FpZFhKc0lqb2dJbWgwZEhCek9pOHZhSFIwY0hNdkwyUmxiVzh0YldWeVkyaGhiblF1WlhoaGJYQnNaUzl3Y21sMllXTjVJbjBzSUhzaWRIbHdaU0k2SUNKMFpYSnRjMTl2Wmw5elpYSjJhV05sSWl3Z0luVnliQ0k2SUNKb2RIUndjem92TDJoMGRIQnpMeTlrWlcxdkxXMWxjbU5vWVc1MExtVjRZVzF3YkdVdmRHOXpJbjFkZlEuUC1WS3poeUp1bzktUlBpTjVheW5naDdmTFVLY09QQWVaejczU09Zd2Q1UDlZWG1HTE9yTFRXeGdYdkd5UVF0dERETTVELUc0czE5dnhfVTY1ZHJ1UmciXQ~
```

### オープン Mandate に連結したクローズド Mandate

委任された SD-JWT の処理後、オープンな Checkout Mandate にクローズドな Checkout Mandate を連結できます。開示情報を使って、制約のうち該当する情報だけを提示します。

```json
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "example+sd-jwt",
      "kid": "agent-provider-key-1"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "QtXTJtWqg999CmUWGjHFTWMkRPguDfeK3wGSaInd-dw"
        }
      ],
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "y3aocAD2rhYpJQOUMN016faDFGkTBGEDVl1R1TRHdbw",
      "decoded": [
        "4n3L_-3_Fm2GgyFAF8Ct_g",
        {
          "id": "supershoe_limited_edition_gold_sneaker_womens_9_0",
          "title": "SuperShoe Limited Edition Gold"
        }
      ]
    },
    {
      "digest": "a5UMAdxCk_MRayyVdRhpIAZ0ZhjVLEq1g2BWyruKUwg",
      "decoded": [
        "2zPL6vqLBg2WYAdbW9-1lQ",
        {
          "id": "merchant_1",
          "name": "Demo Merchant",
          "website": "https://demo-merchant.example"
        }
      ]
    },
    {
      "digest": "QtXTJtWqg999CmUWGjHFTWMkRPguDfeK3wGSaInd-dw",
      "decoded": [
        "laAoWKNRuGnwREjJWYJ7pg",
        {
          "vct": "mandate.checkout.open.1",
          "constraints": [
            {
              "type": "checkout.line_items",
              "items": [
                {
                  "id": "line_1",
                  "acceptable_items": [
                    {
                      "...": "y3aocAD2rhYpJQOUMN016faDFGkTBGEDVl1R1TRHdbw"
                    }
                  ],
                  "quantity": 1
                }
              ]
            },
            {
              "type": "checkout.allowed_merchants",
              "allowed": [
                {
                  "...": "a5UMAdxCk_MRayyVdRhpIAZ0ZhjVLEq1g2BWyruKUwg"
                }
              ]
            }
          ],
          "cnf": {
            "jwk": {
              "crv": "P-256",
              "kty": "EC",
              "x": "QpSyxPQHy38xckypDr54gZ3T42zj9iLtV4koyb5U27c",
              "y": "37HLd7JJinxjJIn8J7HijssoeclbfhdW-gUL7feI9lw"
            }
          },
          "iat": 1777342357,
          "exp": 1777345957
        }
      ]
    }
  ]
}
{
  "issuer_signed_jwt": {
    "header": {
      "alg": "ES256",
      "typ": "kb+sd-jwt"
    },
    "payload": {
      "delegate_payload": [
        {
          "...": "7VLY-eKTFSShLoZRXY5jXcD2UHm1JvPmoANYRqqxy34"
        }
      ],
      "iat": 1777342376,
      "aud": "merchant",
      "nonce": "b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4",
      "sd_hash": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8",
      "_sd_alg": "sha-256"
    }
  },
  "disclosures": [
    {
      "digest": "7VLY-eKTFSShLoZRXY5jXcD2UHm1JvPmoANYRqqxy34",
      "decoded": [
        "szhpxKrgGJwyqMEN9WI5Sw",
        {
          "_sd": [
            "3A9UyZJofw2eMP-Lx2tYaNpCcuB8elnhwwLhZLwqFFM"
          ],
          "vct": "mandate.checkout.1",
          "checkout_hash": "NivWhuqfzcvZNapvIEJ2-3tsdQLkiuIcye2g46WVgX8"
        }
      ]
    },
    {
      "digest": "FzLoxbbtgQGYZxoSM2NJYJtkFTSsdfUBoVEQ12k7JN8",
      "decoded": [
        "w-n1leFT6z8rHTNHwr5Wow",
        "checkout_jwt",
        {
          "header": {
            "alg": "ES256",
            "typ": "JWT"
          },
          "payload": {
            "order_id": "09414145-b7bi-432e-bf5c-ha0ba0bc4580",
            "merchant": {
              "id": "merchant_1",
              "name": "Demo Merchant",
              "website": "https://demo-merchant.example"
            },
            "line_items": [
              {
                "id": "line_1",
                "product": {
                  "id": "supershoe_limited_edition_gold_sneaker_womens_9_0",
                  "title": "SuperShoe Limited Edition Gold — Women's 9",
                  "price": 199.0,
                  "currency": "USD"
                },
                "quantity": 1
              }
            ],
            "total_price": 199.0,
            "currency": "USD",
            "shipping_policy": "Standard Shipping",
            "return_policy": "30-day returns"
          }
        }
      ]
    }
  ]
}
```

#### エンコード済みトークン

```
eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImV4YW1wbGUrc2Qtand0IiwgImtpZCI6ICJhZ2VudC1wcm92aWRlci1rZXktMSJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIlF0WFRKdFdxZzk5OUNtVVdHakhGVFdNa1JQZ3VEZmVLM3dHU2FJbmQtZHcifV0sICJfc2RfYWxnIjogInNoYS0yNTYifQ.HvCGk7ye_c0LN2-NFG13wfyu3LA--rckTPGm36ugO2aRvsded7ngw1py8W3JF7wBpoQnsKr17tNTF3zLeYcoWA~WyI0bjNMXy0zX0ZtMkdneUZBRjhDdF9nIiwgeyJpZCI6ICJzdXBlcnNob2VfbGltaXRlZF9lZGl0aW9uX2dvbGRfc25lYWtlcl93b21lbnNfOV8wIiwgInRpdGxlIjogIlN1cGVyU2hvZSBMaW1pdGVkIEVkaXRpb24gR29sZCJ9XQ~WyIyelBMNnZxTEJnMldZQWRiVzktMWxRIiwgeyJpZCI6ICJtZXJjaGFudF8xIiwgIm5hbWUiOiAiRGVtbyBNZXJjaGFudCIsICJ3ZWJzaXRlIjogImh0dHBzOi8vZGVtby1tZXJjaGFudC5leGFtcGxlIn1d~WyJsYUFvV0tOUnVHbndSRWpKV1lKN3BnIiwgeyJ2Y3QiOiAibWFuZGF0ZS5jaGVja291dC5vcGVuLjEiLCAiY29uc3RyYWludHMiOiBbeyJ0eXBlIjogImNoZWNrb3V0LmxpbmVfaXRlbXMiLCAiaXRlbXMiOiBbeyJpZCI6ICJsaW5lXzEiLCAiYWNjZXB0YWJsZV9pdGVtcyI6IFt7Ii4uLiI6ICJ5M2FvY0FEMnJoWXBKUU9VTU4wMTZmYURGR2tUQkdFRFZsMVIxVFJIZGJ3In1dLCAicXVhbnRpdHkiOiAxfV19LCB7InR5cGUiOiAiY2hlY2tvdXQuYWxsb3dlZF9tZXJjaGFudHMiLCAiYWxsb3dlZCI6IFt7Ii4uLiI6ICJhNVVNQWR4Q2tfTVJheXlWZFJocElBWjBaaGpWTEVxMWcyQld5cndLVXdnIn1dfV0sICJjbmYiOiB7Imp3ayI6IHsiY3J2IjogIlAtMjU2IiwgImt0eSI6ICJFQyIsICJ4IjogIlFwU3l4UFFIeTM4eGNreXZEcjU0Z1ozVDQyemo5aUx0VjRrb3liNVUyN2MiLCAieSI6ICIzN0hMZDdKSmlueGpKSW44SjdIaWpzc29lY0JsZmhkVy1nVUw3ZmVJOWx3In19LCAiaWF0IjogMTc3NzM0MjM1NywgImV4cCI6IDE3NzczNDU5NTd9XQ~~eyJhbGciOiAiRVMyNTYiLCAidHlwIjogImtiK3NkLWp3dCJ9.eyJkZWxlZ2F0ZV9wYXlsb2FkIjogW3siLi4uIjogIjdWTFktZUtURlNTaExvWlJYWTVqWGNEMlVIbTFKdlBtb0FOWVJxcXh5MzQifV0sICJpYXQiOiAxNzc3MzQyMzc2LCAiYXVkIjogIm1lcmNoYW50IiwgIm5vbmNlIjogImI5YzhkN2U2ZjVhNGIzYzJkMWUwZjlhOGI3YzZkNWU0IiwgInNkX2hhc2giOiAiRnpMb3hiYnRnUUdZWnhvU00yTkpZSnRrRlRTc2RmVUJvVkVRMTJrN0pOOCIsICJfc2RfYWxnIjogInNoYS0yNTYifQ.lSjkli6K3NbKlWOl1gJdWDwiyL88yJVyx32ZJHmvCXfRoItnchXw-MLUDEJv7o9lmTeipS42qNt7Z_oGSnRH1w~WyJzeGhweEtyZ0dKd3lxTUVNOVdJNVN3IiwgeyJfc2QiOiBbIjNBOVV5WkpvZncyZU1QLUx4MnRZYU5wQ2N1QjhlbG5od3dMaFpMd3FRRk0iXSwgInZjdCI6ICJtYW5kYXRlLmNoZWNrb3V0LjEiLCAiY2hlY2tvdXRfaGFzaCI6ICJOaXZXaHVxZnpjdlpOYXB2SUVKMi0zdHNkUUxraXVJY3llMmc0NldWZ1g4In1d~WyJ3LW4xbGVGVDZ6OHJIVE5Id3I1V293IiwgImNoZWNrb3V0X2p3dCIsICJleUpoYkdjaU9pQWlSVk15TlRZaUxDQWlkSGx3SWpvZ0lrcFhWQ0lzSUNKcmFXUWlPaUFpYldWeVkyaGhiblF0YTJWNUxURWlmUS5leUpwWkNJNklDSXdPVFF4TkRFME5TMWlOekJpTFRRNE0yRXRZamcxWXkxaFlUQm1ZVEJqTkRVNE1EQWlMQ0FpYldWeVkyaGhiblFpT2lCN0ltbGtJam9nSW0xbGNtTm9ZVzUwWHpFaUxDQWlibUZ0WlNJNklDSkVaVzF2SUUxbGNtTm9ZVzUwSWl3Z0luZGxZbk5wZEdVaU9pQWlhSFIwY0hNNkx5OWtaVzF2TFcxbGNtTm9ZVzUwTG1WNFlXMXdiR1VpZlN3Z0lteHBibVZmYVhSbGJYTWlPaUJiZXlKcFpDSTZJQ0pzYVY4d0lpd2dJbWwwWlcwaU9pQjdJbWxrSWpvZ0luTjFjR1Z5YzJodlpWOXNhVzFwZEdWa1gyVmthWFJwYjI1ZloyOXNaRjl6Ym1WaGEyVnlYM2R2YldWdWMxODVYekFpTENBaWRHbDBiR1VpT2lBaVUzVndaWEp6YUc5bElFeHBiV2wwWldRZ1JXUnBkR2x2YmlCSGIyeGtJRk51WldGclpYSWdWMjl0Wlc1eklEa2lMQ0FpY0hKcFkyVWlPaUF4T1Rrd01IMHNJQ0p4ZFdGdWRHbDBlU0k2SURFc0lDSjBiM1JoYkhNaU9pQmJleUowZVhCbElqb2dJbk4xWW5SdmRHRnNJaXdnSW1GdGIzVnVkQ0k2SURFNU9UQXdmU3dnZXlKMGVYQmxJam9nSW5SdmRHRnNJaXdnSW1GdGIzVnVkQ0k2SURFNU9UQXdmVjE5WFN3Z0luTjBZWFIxY3lJNklDSnBibU52YlhCc1pYUmxJaXdnSW1OMWNuSmxibU41SWpvZ0lsVlRSQ0lzSUNKMGIzUmhiSE1pT2lCYmV5SjBlWEJsSWpvZ0luTjFZblJ2ZEdGc0lpd2dJbUZ0YjNWdWRDSTZJREU1T1RBd2ZTd2dleUowZVhCbElqb2dJblJ2ZEdGc0lpd2dJbUZ0YjNWdWRDSTZJREU1T1RBd2ZWMHNJQ0pzYVc1cmN5STZJRnQ3SW5SNWNHVWlPaUFpY0hKcGRtRmplVjl3YjJ4cFkza2lMQ0FpZFhKc0lqb2dJbWgwZEhCek9pOHZhSFIwY0hNdkwyUmxiVzh0YldWeVkyaGhiblF1WlhoaGJYQnNaUzl3Y21sMllXTjVJbjBzSUhzaWRIbHdaU0k2SUNKMFpYSnRjMTl2Wmw5elpYSjJhV05sSWl3Z0luVnliQ0k2SUNKb2RIUndjem92TDJoMGRIQnpMeTlrWlcxdkxXMWxjbU5vWVc1MExtVjRZVzF3YkdVdmRHOXpJbjFkZlEuUC1WS3poeUp1bzktUlBpTjVheW5naDdmTFVLY09QQWVaejczU09Zd2Q1UDlZWG1HTE9yTFRXeGdYdkd5UVF0dERETTVELUc0czE5dnhfVTY1ZHJ1UmciXQ~
```

## 共通型

### Item

Checkout 内の商品またはサービスを表します。

### LineItemRequirements

Checkout の明細項目に求める条件を表します。

### Merchant

販売者を識別する情報を表します。
